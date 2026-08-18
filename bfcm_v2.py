import hashlib
import secrets
import json
import uuid

def list_events():
    
    events = []

    with open("event_log.json", "r") as f:
        for line in f:
            event = json.loads(line)
            events.append(event)

    print("\nAvailable Events:\n")

    for event in events:
        print(f'{event["event_id"]}: '
              f'{event["question"]}')

    return events

def choose_event():

    events = list_events()

    chosen_id = input("\nSelect Event ID: ")

    for event in events:

        if event["event_id"] == chosen_id:
            return event

    print("Invalid event selected.")
    return None

def create_event(event_id, content):
    event_data = {"event_id": event_id,
                  "question": content}
    
    with open("event_log.json", "a") as f:
        f.write(json.dumps(event_data) + "\n")

def get_user_input():
    event = choose_event()

    if event is None:
        return None, None

    prediction = input(f'Enter prediction for: '
                       f'{event["question"]}')

    return event["event_id"], prediction

def serialize_commitment(event_id, prediction, nonce):
    return f"{event_id}|{prediction}|{nonce}"

def generate_nonce():
    return secrets.token_hex(16)

def create_commitment(event_id, prediction, nonce):
    message = serialize_commitment(event_id, prediction, nonce)
    return hashlib.sha256(message.encode("utf-8")).hexdigest()

def save_prediction_public(prediction_id, event_id, commitment):
    data = {"prediction_id": prediction_id,
            "event_id": event_id,
            "commitment": commitment}
    
    with open("predictions_public.json", "a") as f:
        f.write(json.dumps(data) + "\n")

def save_prediction_private(prediction_id, event_id, nonce, prediction):
    data = {"prediction_id": prediction_id,
            "event_id": event_id,
            "nonce": nonce,
            "prediction": prediction}
    
    with open("predictions_private.json", "a") as f:
        f.write(json.dumps(data) + "\n")

def verify(prediction_id):
    
    public_record = None
    private_record = None

    with open("predictions_public.json", "r") as f_pu:
        for line in f_pu: 
            # print(line)
            public_data = json.loads(line)

            if public_data["prediction_id"] == prediction_id:
                public_record = public_data
                break

    with open("predictions_private.json", "r") as f_pr:
        for line in f_pr:
            # print(line)
            verification_data = json.loads(line)

            if verification_data["prediction_id"] == prediction_id:
                private_record = verification_data
                break

    if public_record is None or private_record is None:
        print("MISSING DATA")
        return False

    message = serialize_commitment(private_record["event_id"], private_record["prediction"], private_record["nonce"])

    verify_hash = hashlib.sha256(message.encode("utf-8")).hexdigest()

    stored_commitment = public_record["commitment"]

    if verify_hash == stored_commitment:
        print("Verification Valid")
        return True
    else:
        print("Verification Invalid")
        return False
    
def main():
    event_id, prediction = get_user_input()

    nonce = generate_nonce()

    prediction_id = str(uuid.uuid4())

    commitment = create_commitment(event_id, prediction, nonce)

    print(f"\nCommitment: {commitment}")

    save_prediction_public(prediction_id, event_id, commitment)

    save_prediction_private(prediction_id, event_id, nonce, prediction)

    verify(prediction_id)

if __name__=="__main__":
    main()
