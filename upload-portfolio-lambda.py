import boto3
import io
import zipfile
import mimetypes

def lambda_handler(event, context):

    try:
        s3 = boto3.resource('s3')
        sns = boto3.resource('sns')

        portfolio_bucket = s3.Bucket('portfolio.net17research.com')
        build_bucket = s3.Bucket('portfoliobuild.net17research.com')
        topic = sns.Topic('arn:aws:sns:us-east-1:516336414748:deployPortfolioTopic')

        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                  ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print("Job complete.")
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio deployed successfully!")
    except:
        topic.publish(Subject="Portfolio Deplo Failure", Message="Portfolio not deployed successfully!")
        raise

    return 'Update Complete'
