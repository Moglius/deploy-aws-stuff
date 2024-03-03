import json

import jwt


def lambda_handler(event, context):
    # TODO implement
    print(event)

    # Retrieve request parameters from the Lambda function input:
    encoded_token = event["headers"]["authorization"]

    decoded_token = jwt.decode(
        encoded_token, algorithms=["RS256"], options={"verify_signature": False}
    )

    if "appid" in decoded_token:
        client_app_id = decoded_token["appid"]
    else:
        print("You're not authorized here, go away!!")
        return {"statusCode": 401, "body": json.dumps("401 (Unauthorized)")}

    if "roles" in decoded_token:
        client_roles = decoded_token["roles"]
    else:
        print("You're not authorized here, go away!!")
        return {"statusCode": 401, "body": json.dumps("401 (Unauthorized)")}

    print("app_id", client_app_id)
    print("client_roles", client_roles)

    if "read.things" in client_roles:
        print("call step function here")
        return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
    else:
        print("You're not authorized here, go away!!")
        return {"statusCode": 401, "body": json.dumps("401 (Unauthorized)")}
