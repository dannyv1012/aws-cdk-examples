'''
Example waf module. If you are deploying this for use with cloudfront
then remember to deploy it to us-east-1 (same region where cloudfront 
distros are created).
'''
from constructs import Construct
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_wafv2 as wafv2
)

class Wafs(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define waf rules. 
        waf_rules=[
            wafv2.CfnWebACL.RuleProperty(
                # Geo restriction rule. NOTE: If you are using the waf for cloudfront then 
                # don't include this rule as geo restriction is applied within the 
                # cloudfront distribution and not via waf.
                name="geo-restrict", 
                priority=0,
                action=wafv2.CfnWebACL.RuleActionProperty(
                    block = {} 
                ),
                visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name=f'example',
                    sampled_requests_enabled=True
                ),
                statement=wafv2.CfnWebACL.StatementProperty(
                    geo_match_statement=wafv2.CfnWebACL.GeoMatchStatementProperty(
                        # Add whichever additional country codes needed.
                        country_codes=[
                            "RU" 
                        ]
                    )
                )                    
            ),
            wafv2.CfnWebACL.RuleProperty(
                name="ip-block-list", # Rule that blocks certain IPs
                priority=1,
                action=wafv2.CfnWebACL.RuleActionProperty(
                    block = {} 
                ),
                visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name='ip-block-list',
                    sampled_requests_enabled=True
                ),
                statement=wafv2.CfnWebACL.StatementProperty(
                    # Example of an OR statement. Waf blocks the traffic 
                    # if the incoming IP matches one of the IP sets 
                    # specified.
                    or_statement=wafv2.CfnWebACL.OrStatementProperty(
                        statements=[ 
                            wafv2.CfnWebACL.StatementProperty(
                                ip_set_reference_statement={
                                    'arn': 'arn_of_ip_set'
                                } 
                            ),
                            wafv2.CfnWebACL.StatementProperty(
                                ip_set_reference_statement={
                                    'arn': 'arn_of_ip_set'
                                } 
                            )
                        ]
                    )
                )                 
            ),
            wafv2.CfnWebACL.RuleProperty(
                name="rate-limit", # Rate limiting example
                priority=2,
                action=wafv2.CfnWebACL.RuleActionProperty(
                    block = {} 
                ),
                visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name='rate-limit',
                    sampled_requests_enabled=True
                ),
                statement=wafv2.CfnWebACL.StatementProperty(
                    rate_based_statement = wafv2.CfnWebACL.RateBasedStatementProperty(
                    limit              = 1000,
                    aggregate_key_type = "IP"
                    ) 
                )                   
            ),
            wafv2.CfnWebACL.RuleProperty(
                # Example of a managed rule
                name="AWSManagedRulesAmazonIpReputationList", 
                priority=5,
                override_action=wafv2.CfnWebACL.OverrideActionProperty(
                    none={}
                ),
                visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name='AWSManagedRulesAmazonIpReputationList',
                    sampled_requests_enabled=True
                ),
                statement=wafv2.CfnWebACL.StatementProperty(
                    managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                        name="AWSManagedRulesAmazonIpReputationList",
                        vendor_name="AWS"
                    )   
                )
            ),
            wafv2.CfnWebACL.RuleProperty(
                name="AWSManagedRulesSQLiRuleSet",
                priority=10,
                override_action=wafv2.CfnWebACL.OverrideActionProperty(
                    none={}
                ),
                visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name='AWSManagedRulesSQLiRuleSet',
                    sampled_requests_enabled=True
                ),
                statement=wafv2.CfnWebACL.StatementProperty(
                    managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                        name="AWSManagedRulesSQLiRuleSet",
                        vendor_name="AWS"
                    )   
                )
            ),
            wafv2.CfnWebACL.RuleProperty(
                name="AWSManagedRulesKnownBadInputsRuleSet",
                priority=15,
                override_action=wafv2.CfnWebACL.OverrideActionProperty(
                    none={}
                ),
                visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name='AWSManagedRulesKnownBadInputsRuleSet',
                    sampled_requests_enabled=True
                ),
                statement=wafv2.CfnWebACL.StatementProperty(
                    managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                        name="AWSManagedRulesKnownBadInputsRuleSet",
                        vendor_name="AWS"
                    )   
                )
            )
        ] 
        

        # Define waf
        waf = wafv2.CfnWebACL(self, 'waf',
            scope='REGIONAL', # set to 'CLOUDFRONT' if using the waf for cloudfront
            description=f'example waf',
            name='example-waf',
            # This default actions allows traffic if no rules were matched
            default_action=wafv2.CfnWebACL.DefaultActionProperty(
                allow=wafv2.CfnWebACL.AllowActionProperty(),
                block=None
            ),
            # Uncomment if you want the default action to be block instead
            # default_action=wafv2.CfnWebACL.DefaultActionProperty(
            #     allow=None,
            #     block=wafv2.CfnWebACL.BlockActionProperty()
            # ),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name='example-waf',
                sampled_requests_enabled=True
            ),
            rules=waf_rules
        )

        # Output waf arn
        CfnOutput(self, 'waf_arn', 
            value=waf.attr_arn, 
            export_name=f'example-waf-arn'
        )
        
        