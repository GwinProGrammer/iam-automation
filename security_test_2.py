import boto3
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# Config - customize these
FAILED_LOGIN_THRESHOLD = 5  # number of failed logins to alert
FAILED_LOGIN_WINDOW_MINUTES = 15  # time window to count failures

BUSINESS_HOURS_START = 8  # 8 AM
BUSINESS_HOURS_END = 18   # 6 PM

ALLOWED_IP_RANGES = [        # Example: only allow these CIDR blocks (adjust to your org)
    "203.0.113.0/24",
    "198.51.100.0/24",
]

# Utility to check if IP is in allowed ranges
import ipaddress
def ip_allowed(ip):
    ip_addr = ipaddress.ip_address(ip)
    for cidr in ALLOWED_IP_RANGES:
        if ip_addr in ipaddress.ip_network(cidr):
            return True
    return False

def is_outside_business_hours(event_time):
    local_hour = event_time.astimezone().hour  # convert to local timezone
    return local_hour < BUSINESS_HOURS_START or local_hour >= BUSINESS_HOURS_END

def main():
    client = boto3.client('cloudtrail')

    # Define time range to look back (e.g., last 24 hours)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=24)

    # Get login events: 'ConsoleLogin' eventName is used for sign-in attempts
    response = client.lookup_events(
        LookupAttributes=[{'AttributeKey': 'EventName', 'AttributeValue': 'ConsoleLogin'}],
        StartTime=start_time,
        EndTime=end_time,
        MaxResults=1000
    )

    failed_logins = defaultdict(list)  # user -> list of failure timestamps
    suspicious_access = []

    for event in response['Events']:
        event_detail = event['CloudTrailEvent']
        # CloudTrailEvent is a JSON string - parse it
        import json
        detail = json.loads(event_detail)

        user_identity = detail.get('userIdentity', {})
        user_name = user_identity.get('userName', 'Unknown')

        event_time = datetime.fromisoformat(detail['eventTime'].replace('Z', '+00:00'))

        # Detect failed login
        login_result = detail.get('responseElements', {}).get('ConsoleLogin')
        # Sometimes, the key might be missing or null, treat missing or "Failure" as failed login
        if login_result != "Success":
            failed_logins[user_name].append(event_time)

        # Detect unusual access time
        if not is_outside_business_hours(event_time):
            # inside business hours, no alert
            pass
        else:
            ip = detail.get('sourceIPAddress')
            suspicious_access.append({
                'user': user_name,
                'time': event_time,
                'ip': ip,
                'reason': 'Outside business hours'
            })

        # Detect unusual IP
        ip = detail.get('sourceIPAddress')
        if ip and not ip_allowed(ip):
            suspicious_access.append({
                'user': user_name,
                'time': event_time,
                'ip': ip,
                'reason': 'IP not in allowed ranges'
            })

    # Analyze failed login spikes
    for user, times in failed_logins.items():
        times = sorted(times)
        # Sliding window check for FAILED_LOGIN_THRESHOLD failures in FAILED_LOGIN_WINDOW_MINUTES
        for i in range(len(times)):
            window_start = times[i]
            window_end = window_start + timedelta(minutes=FAILED_LOGIN_WINDOW_MINUTES)
            count = sum(1 for t in times if window_start <= t <= window_end)
            if count >= FAILED_LOGIN_THRESHOLD:
                print(f"ALERT: User '{user}' had {count} failed login attempts between {window_start} and {window_end}. Possible brute force attack.")
                break

    # Print suspicious access alerts
    for alert in suspicious_access:
        print(f"ALERT: Suspicious login for user '{alert['user']}' at {alert['time']} from IP {alert['ip']} - Reason: {alert['reason']}")

if __name__ == "__main__":
    main()
