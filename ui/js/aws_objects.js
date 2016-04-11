// Setting AWS Dynamo Credentials
AWS.config.update({accessKeyId: 'AKIAIDNNNRKSEKJB6FXQ', secretAccessKey: '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'});
var s3 = new AWS.S3();

AWS.config.region = 'us-west-1';
var table = new AWS.DynamoDB({params: {TableName: 'SMARTCAM'}});
