import sys
from streamlit.web.cli import main

if __name__ == "__main__":
    # Point sys.argv to the streamlit run command and your main app file
    sys.argv = [
        "streamlit",
        "run",
        "app.py",  # Replace with your actual Streamlit main file name
        "--global.developmentMode=false",
    ]
    main()
