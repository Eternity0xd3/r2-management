from r2_management import R2Management
import terminal_ui, cli

from dotenv import load_dotenv
import os, sys

def check_env_vars():
    required_vars = ["BUCKET", "PUBLIC_URL", "ENDPOINT", "ACCESS_KEY", "SECRET_ACCESS_KEY"]
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

def determine_mode(r2):
    args = sys.argv[1:]

    if not args:
        terminal_ui.start_app(r2)
    else:
        cli.run(r2, args)

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

    determine_mode(r2_management)

if __name__ == "__main__":
    main()