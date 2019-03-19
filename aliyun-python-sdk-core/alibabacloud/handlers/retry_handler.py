# Copyright 2019 Alibaba Cloud Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
from alibabacloud.handlers import RequestHandler
import aliyunsdkcore.retry.retry_policy as retry_policy
from aliyunsdkcore.retry.retry_condition import RetryCondition
from aliyunsdkcore.retry.retry_policy_context import RetryPolicyContext
import aliyunsdkcore.utils
import aliyunsdkcore.utils.parameter_helper
import aliyunsdkcore.utils.validation


class RetryHandler(RequestHandler):

    def _add_request_client_token(self, api_request):
        # TODO implement: add a ClientToken parameter on api_request
        pass

    def handle_request(self, context):
        retry_policy_context = RetryPolicyContext(context.api_request, None, 0, None)
        if context.client.retry_policy.should_retry(retry_policy_context) & \
                RetryCondition.SHOULD_RETRY_WITH_CLIENT_TOKEN:
            self._add_request_client_token(context.api_request)
        context.http_request.retries = 0

    def handle_response(self, context):
        api_request = context.api_request
        retry_policy_context = RetryPolicyContext(api_request, context.exception,
                                                  context.http_request.retries,
                                                  context.http_response.status_code)

        should_retry = context.client.retry_policy.should_retry(retry_policy_context)

        if should_retry & RetryCondition.SHOULD_RETRY:
            context.retry_flag = True
            context.retry_backoff = context.client.retry_policy.compute_delay_before_next_retry(
                retry_policy_context
            )
        else:
            context.retry_flag = False
            context.retry_backoff = 0
            if context.exception:
                raise context.exception
        context.http_request.retries += 1

