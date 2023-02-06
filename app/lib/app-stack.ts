import * as cdk from 'aws-cdk-lib'
import { Code, Function, Runtime } from 'aws-cdk-lib/aws-lambda'
import { Construct } from 'constructs'
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha'
import { Duration } from 'aws-cdk-lib'
import { Effect, PolicyStatement } from 'aws-cdk-lib/aws-iam'
import { Rule, Schedule } from 'aws-cdk-lib/aws-events'
import { LambdaFunction } from 'aws-cdk-lib/aws-events-targets'
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class AppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props)

    const stackAnalysisFn = new PythonFunction(this, 'StackAnalysisFn', {
      runtime: Runtime.PYTHON_3_8,
      entry: './lambda/',
      index: 'main.py',
      handler: 'lambda_handler',
      environment: {
        ENVIRONMENT: 'dev',
        IS_AWS_LAMBDA: 'true',
        LOG_LEVEL: 'DEBUG',
      },
      timeout: Duration.minutes(5),
    })

    stackAnalysisFn.addToRolePolicy(
      new PolicyStatement({
        effect: Effect.ALLOW,
        actions: ['ses:SendEmail'],
        resources: ['*'],
      })
    )

    const eventRule = new Rule(this, 'scheduleRule', {
      schedule: Schedule.cron({ minute: '0', hour: '18', month: '*', weekDay: 'MON-FRI', year: '*' }),
    })
    eventRule.addTarget(new LambdaFunction(stackAnalysisFn))
  }
}
