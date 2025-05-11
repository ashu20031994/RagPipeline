# Setting Up the Environment

Follow these steps to create a virtual environment and install the required dependencies:

1. **Create a Virtual Environment**:
    Open a terminal and navigate to your project directory. Run the following command to create a virtual environment:
    ```
    python -m venv env
    ```
    This will create a folder named `env` in your project directory.

2. **Activate the Virtual Environment**:
    - On **Windows**:
      ```
      .\env\Scripts\activate
      ```
    - On **macOS/Linux**:
      ```
      source env/bin/activate
      ```

3. **Install Dependencies**:
    Once the virtual environment is activated, install the required packages using `requirements.txt`:
    ```
    pip install -r requirements.txt
    ```

4. **Run the Application**:
    To run the application using Streamlit, use the following command:
    ```
    streamlit run client.py
    ```
    Make sure you are in the project directory and the virtual environment is activated before running this command.
