# fn_meeting_actions
An AWS lambda that retrieves a meeting transcript from S3 and creates a list of action items from the meeting

This AWS Lambda function retrieves a meeting transcript stored in an S3 bucket, processes the transcript to identify action items, and then returns the list of action items in a response. It utilizes AWS Lambda for serverless compute, Amazon S3 for storage, and the Bedrock Runtime Converse API for generating action items from the transcript.

The default LLM is "amazon.titan-text-express-v1".