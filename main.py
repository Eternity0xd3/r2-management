from r2_management.r2_management import R2Management

from dotenv import load_dotenv
import os

def check_env_vars():
    required_vars = ["BUCKET", "PUBLIC_URL", "ENDPOINT", "ACCESS_KEY", "SECRET_ACCESS_KEY"]
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

def main():
    load_dotenv()
    check_env_vars()

    r2_management = R2Management(
        bucket_name=os.getenv("BUCKET"),
        endpoint_url=os.getenv("ENDPOINT"),
        access_key=os.getenv("ACCESS_KEY"),
        secret_key=os.getenv("SECRET_ACCESS_KEY"),
        public_url=os.getenv("PUBLIC_URL")
    )

    print(r2_management.list())

if __name__ == "__main__":
    main()