import uvicorn
from workflow import app, wfr
from time import sleep


def main():
    try:
        wfr.start()
        sleep(5)  # wait for workflow runtime to start

        uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
    except Exception as e:
        print(f"Error during application startup: {e}")


if __name__ == "__main__":
    main()
