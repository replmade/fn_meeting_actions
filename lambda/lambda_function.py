# Use the Converse API to send a text message to the LLM
import os
import boto3
from botocore.exceptions import ClientError

# Create an Amazon S3 client.
s3 = boto3.client("s3")

# Create a Bedrock Runtime client
bedrock_runtime = boto3.client("bedrock-runtime")

# Set the model ID, e.g., Anthropic Claude Sonnet 3.5.
model_id = os.environ["MODEL_ID"]


def lambda_handler(event, context):
    for transcript_key in event["Records"]:
        transcript_key = transcript_key["s3"]["object"]["key"]

        # Extract the meeting transcript from the event.
        try:
            meeting_transcript_obj = s3.get_object(
                Bucket=os.environ["TRANSCRIPTS_S3_BUCKET"],
                Key=transcript_key,
            )
        except ClientError as e:
            error_message = f"ERROR: Unable to retrieve object {transcript_key} from S3. Reason: {e}"
            print(error_message)
            return {
                "statusCode": 500,
                "body": error_message,
            }
        meeting_transcript = meeting_transcript_obj["Body"].read().decode("utf-8")
        print(meeting_transcript)

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

            # Define the new S3 key for the action items file.
            action_items_key = f"actions/{transcript_key.split('/')[-1]}"

            # Save the response text to the new S3 key.
            s3.put_object(
                Bucket=os.environ["TRANSCRIPTS_S3_BUCKET"],
                Key=action_items_key,
                Body=response_text.encode("utf-8"),
            )

            # Construct the S3 URL for the newly created file.
            s3_url = f"https://{os.environ['TRANSCRIPTS_S3_BUCKET']}.s3.amazonaws.com/{action_items_key}"

            return {
                "statusCode": 200,
                "body": f"Action items saved successfully. File URL: {s3_url}",
            }

        except (ClientError, Exception) as e:
            return {
                "statusCode": 500,
                "body": f"ERROR: Can't invoke '{model_id}'. Reason: {e}",
            }
