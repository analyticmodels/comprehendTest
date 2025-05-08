import csv
import random
import uuid
from faker import Faker
import pandas as pd
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Set random seed for reproducibility
random.seed(42)
fake.seed_instance(42)

# Number of rows to generate
NUM_ROWS = 1000

def generate_pii_dataset():
    """Generate a dataset with columns that may contain PII for testing redaction tools."""
    
    data = []
    
    # List of PII types to include
    pii_types = [
        "name", "phone", "ssn", "address", "email", 
        "credit_card", "date_time", "url", "ip"
    ]
    
    # Templates for sentences with PII
    sentence_templates = [
        "Please contact {name} at {phone} for more information.",
        "My name is {name} and I live at {address}.",
        "Send the report to {email} by tomorrow.",
        "The meeting with {name} is scheduled for {date_time}.",
        "My social security number is {ssn}, please update your records.",
        "The payment was processed using card ending in {credit_card_last4}.",
        "You can find more information at {url}.",
        "The server at {ip} needs to be restarted.",
        "Please transfer $500 to account holder {name}.",
        "The new website can be accessed at {url} starting tomorrow.",
        "{name} requested access to file #12345.",
        "The appointment is confirmed for {date_time}.",
        "Customer support can be reached at {phone}.",
        "The delivery will be made to {address}.",
        "Login credentials were sent to {email}.",
        "The user connected from IP address {ip}."
    ]
    
    # Templates for sentences without PII
    non_pii_sentences = [
        "The project deadline is approaching quickly.",
        "Please review the attached documents.",
        "The system update was completed successfully.",
        "We need to discuss the quarterly results.",
        "The meeting agenda has been updated.",
        "Please confirm receipt of this message.",
        "The product specifications have been revised.",
        "Customer satisfaction has improved this quarter.",
        "The new policy takes effect next month.",
        "All employees must complete the training.",
        "The research findings were inconclusive.",
        "The factory will be closed for maintenance.",
        "The report highlights several key issues.",
        "We've received positive feedback from users.",
        "The software release has been delayed.",
        "The committee approved all recommendations."
    ]
    
    for i in range(NUM_ROWS):
        # Generate unique ID
        unique_id = str(uuid.uuid4())
        
        # Determine if sentence will contain PII (60% chance)
        has_pii_in_sentence = random.random() < 0.6
        
        # Generate sentence
        if has_pii_in_sentence:
            template = random.choice(sentence_templates)
            sentence = template
            
            # Replace PII placeholders in the template
            if "{name}" in sentence:
                sentence = sentence.replace("{name}", fake.name())
            if "{phone}" in sentence:
                sentence = sentence.replace("{phone}", fake.phone_number())
            if "{ssn}" in sentence:
                sentence = sentence.replace("{ssn}", fake.ssn())
            if "{address}" in sentence:
                sentence = sentence.replace("{address}", fake.address().replace('\n', ', '))
            if "{email}" in sentence:
                sentence = sentence.replace("{email}", fake.email())
            if "{credit_card_last4}" in sentence:
                sentence = sentence.replace("{credit_card_last4}", fake.credit_card_number()[-4:])
            if "{date_time}" in sentence:
                random_date = fake.date_time_between(start_date="-1y", end_date="now")
                sentence = sentence.replace("{date_time}", random_date.strftime("%Y-%m-%d %H:%M:%S"))
            if "{url}" in sentence:
                sentence = sentence.replace("{url}", fake.url())
            if "{ip}" in sentence:
                sentence = sentence.replace("{ip}", fake.ipv4())
        else:
            sentence = random.choice(non_pii_sentences)
        
        # Generate info1 through info4 columns
        info_columns = []
        for j in range(4):
            # Determine if this info column will contain PII (40% chance)
            if random.random() < 0.4:
                pii_type = random.choice(pii_types)
                
                if pii_type == "name":
                    info_value = fake.name()
                elif pii_type == "phone":
                    info_value = fake.phone_number()
                elif pii_type == "ssn":
                    info_value = fake.ssn()
                elif pii_type == "address":
                    info_value = fake.address().replace('\n', ', ')
                elif pii_type == "email":
                    info_value = fake.email()
                elif pii_type == "credit_card":
                    info_value = fake.credit_card_number()
                elif pii_type == "date_time":
                    random_date = fake.date_time_between(start_date="-1y", end_date="now")
                    info_value = random_date.strftime("%Y-%m-%d %H:%M:%S")
                elif pii_type == "url":
                    info_value = fake.url()
                elif pii_type == "ip":
                    info_value = fake.ipv4()
            else:
                # Non-PII values
                non_pii_options = [
                    "approved", "pending", "rejected",
                    "high", "medium", "low",
                    str(random.randint(1, 100)),
                    f"category_{random.choice('ABCDE')}",
                    f"dept_{random.randint(10, 99)}",
                    fake.word()
                ]
                info_value = random.choice(non_pii_options)
            
            info_columns.append(info_value)
        
        # Add row to dataset
        data.append([unique_id, sentence] + info_columns)
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=["unique_id", "sentence", "info1", "info2", "info3", "info4"])
    
    return df

def main():
    # Generate the dataset
    print("Generating PII dataset...")
    df = generate_pii_dataset()
    
    # Save to CSV
    output_file = "data/pii_test_faker.csv"
    df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
    
    print(f"Dataset created with {len(df)} rows and saved to {output_file}")
    
    # Show sample of the dataset
    print("\nSample of the dataset:")
    print(df.head())
    
    # Print some statistics
    pii_types = ["name", "phone", "ssn", "address", "email", "credit_card", "date_time", "url", "ip"]
    print("\nApproximate PII distribution:")
    
    # Count sentences containing different types of PII
    for pii_type in pii_types:
        count = 0
        for sentence in df['sentence']:
            if pii_type == "name" and any(fake.first_name() in sentence for _ in range(10)):
                count += 1
            elif pii_type == "phone" and any(char.isdigit() and len([c for c in sentence if c.isdigit()]) >= 7 for char in sentence):
                count += 1
            elif pii_type == "ssn" and "ssn" in sentence.lower():
                count += 1
            elif pii_type == "address" and any(word in sentence.lower() for word in ["street", "avenue", "road", "drive", "lane"]):
                count += 1
            elif pii_type == "email" and "@" in sentence:
                count += 1
            elif pii_type == "credit_card" and "card" in sentence.lower():
                count += 1
            elif pii_type == "date_time" and any(month in sentence for month in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]):
                count += 1
            elif pii_type == "url" and any(prefix in sentence.lower() for prefix in ["http", "www", ".com", ".org", ".net"]):
                count += 1
            elif pii_type == "ip" and "ip" in sentence.lower():
                count += 1
        
        print(f"  - {pii_type}: ~{count} sentences")

if __name__ == "__main__":
    main()