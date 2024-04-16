import streamlit as st
import pandas as pd
import numpy as np
from sklearn.datasets import load_breast_cancer, load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.tree import export_graphviz
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
import time
import csv
import os
import random

st.title('Build your own classifiers!')

# Dataset selection
dataset_option = st.selectbox('Select a dataset', ('Breast Cancer', 'Iris'))

if dataset_option == 'Breast Cancer':
    dataset = load_breast_cancer()
    target_names = dataset.target_names
    feature_names = dataset.feature_names
else:
    dataset = load_iris()
    target_names = dataset.target_names
    feature_names = dataset.feature_names

# Create a DataFrame
df = pd.DataFrame(data=dataset.data, columns=feature_names)
df['target'] = dataset.target
df['class'] = pd.Categorical.from_codes(dataset.target, target_names)

if st.checkbox('Show dataframe'):
    st.write(df)

st.subheader('Machine Learning Models')

# User identification
user_id = st.text_input('Enter your user ID:')

# Initialize the interactions list in the session state if it doesn't exist
if 'interactions' not in st.session_state:
    st.session_state.interactions = []

iteration_counter = 0
model_trained = False  # Flag to track if a model has been trained

# Allow users to choose features to train
selected_features = st.multiselect('Select features to train', feature_names, key=f'feature_selection_{iteration_counter}')

if len(selected_features) > 0:
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()  # Record the start time when features are selected

    features = df[selected_features].values
    labels = df['class'].values

    X_train, X_test, y_train, y_test = train_test_split(features, labels, train_size=0.7, random_state=1)

    alg = ['Decision Tree', 'K-Nearest Neighbors', 'Random Forest']
    classifier = st.selectbox('Which algorithm?', alg, key=f'classifier_{iteration_counter}')

    # ... (Existing code for classifier selection and training) ...

    if st.button('Train Model', key=f'train_model_{iteration_counter}'):
        start_time = st.session_state.start_time  # Get the start time from session state
        end_time = time.time()  # Record the end time when the "Train Model" button is clicked
        duration = round(end_time - start_time, 2)

        if classifier == 'Decision Tree':
            dtc.fit(X_train, y_train)
            acc = dtc.score(X_test, y_test)
            tree = export_graphviz(dtc, feature_names=selected_features)
            st.graphviz_chart(tree)
        elif classifier == 'K-Nearest Neighbors':
            knn.fit(X_train, y_train)
            acc = knn.score(X_test, y_test)
        elif classifier == 'Random Forest':
            rfc.fit(X_train, y_train)
            acc = rfc.score(X_test, y_test)

        start_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        end_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
        st.session_state.interactions.append([user_id, start_time_str, end_time_str, duration, dataset_option, ','.join(selected_features), classifier, acc])  # Store the interaction in the session state with dataset information moved before algorithm

        st.write('Accuracy: ', acc)

        # Write interactions to CSV file
        csv_file = f"{user_id}_interactions.csv"
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['User ID', 'Start Time', 'End Time', 'Duration (seconds)', 'Dataset', 'Selected Features', 'Algorithm', 'Accuracy'])  # Include 'Dataset' column before 'Algorithm'
            writer.writerows(st.session_state.interactions)  # Write interactions from the session state

        model_trained = True  # Set the flag to indicate that a model has been trained
        del st.session_state.start_time  # Remove the start time from session state

# Display the interaction log as an option
if st.checkbox('Show interaction log'):
    st.subheader('Interaction Log')
    if len(st.session_state.interactions) > 0:
        log_df = pd.DataFrame(st.session_state.interactions, columns=['User ID', 'Start Time', 'End Time', 'Duration (seconds)', 'Dataset', 'Selected Features', 'Algorithm', 'Accuracy'])  # Include 'Dataset' column before 'Algorithm'
        st.table(log_df)

        # Allow users to download the CSV file
        csv_data = log_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"{user_id}_interactions.csv",
            mime='text/csv'
        )
    else:
        st.write("No interactions recorded.")

# Streamed response emulator
def response_generator():
    responses = [
        "Hello there! How can I assist you today?",
        "Hi, human! Is there anything I can help you with?",
        "Do you need help?",
    ]
    response = random.choice(responses)
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

st.title("AI Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
prompt = st.chat_input("What is up?")

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator())
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
