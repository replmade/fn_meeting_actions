# Use the Converse API to send a text message to the LLM
import os
import boto3
from botocore.exceptions import ClientError

# Create an Amazon S3 client.
s3 = boto3.client("s3")

# Create a Bedrock Runtime client
bedrock_runtime = boto3.client("bedrock-runtime")

# Set the model ID, e.g., Titan Text Premier.
model_id = os.environ["MODEL_ID"]


def lambda_handler(event, context):
    # Extract the meeting transcript from the event.
    meeting_transcript_obj = s3.get_object(
        Bucket=os.environ["TRANSCRIPTS_S3_BUCKET"],
        Key=str(event["transcript_filename"]),
    )
    meeting_transcript = meeting_transcript_obj["Body"].read().decode("utf-8")

    # Start a conversation with the user message.
    user_message = f"""Meeting transcript: 
    {meeting_transcript}
    From the meeting transcript above, Create a list of action items for each person.
    The list should be output in JSON format with an object for each action item. Each
    object should contain a 'person' key with the person's name and an 'action' key 
    with the action item's text.
    """

    conversation = [
        {
            "role": "user",
            "content": [{"text": user_message}],
        }
    ]

    try:
        # Send the message to the model, using a basic inference configuration.
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={
                "maxTokens": 4096,
                "stopSequences": ["User:"],
                "temperature": 0,
                "topP": 1,
            },
            additionalModelRequestFields={},
        )

        # Extract and print the response text.
        response_text = response["output"]["message"]["content"][0]["text"]

        return {"statusCode": 200, "body": response_text}

    except (ClientError, Exception) as e:
        return {
            "statusCode": 500,
            "body": f"ERROR: Can't invoke '{model_id}'. Reason: {e}",
        }
