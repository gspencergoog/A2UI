import uvicorn
import os
import sys

def main():
    # Ensure current directory is in python path to resolve local modules if needed
    sys.path.append(os.getcwd())

    # Run the adk_server app
    # We refer to it by import string local to this directory
    uvicorn.run("adk_server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
