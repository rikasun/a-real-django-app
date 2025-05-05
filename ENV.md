# Environment Variables

# - comet/core/views/core_views.py
# - comet/settings/base.py
AUTH0_CALLBACK_URL=your_value_here

# - comet/core/backends.py
# - comet/core/utils/generic.py
# - comet/core/views/core_views.py
# - comet/settings/base.py
AUTH0_CLIENT_ID=your_value_here

# - comet/settings/base.py
AUTH0_CLIENT_ID_MANAGEMENT=your_value_here

# - comet/core/backends.py
# - comet/core/utils/generic.py
# - comet/settings/base.py
AUTH0_CLIENT_SECRET=your_value_here

# - comet/settings/base.py
AUTH0_CLIENT_SECRET_MANAGEMENT=your_value_here

# - comet/core/backends.py
# - comet/core/utils/generic.py
# - comet/core/views/core_views.py
# - comet/settings/base.py
AUTH0_DOMAIN=your_value_here

# - comet/core/migrations/0001_initial.py
# - comet/core/migrations/0011_slackthread_organization_external_identifier_and_more.py
# - comet/core/migrations/0028_webthread_webthread_unique_openai_thread_id_for_web.py
# - comet/core/migrations/0052_incident_oncall.py
# - comet/core/migrations/0058_remove_incident_status_updates_incidentstatusupdate.py
# - comet/core/migrations/0059_incidentpostmortem.py
# - comet/core/migrations/0064_githubevent_project_repository_full_name_and_more.py
# - comet/core/migrations/0081_reviewmetadata_reviewcontent.py
# - comet/core/migrations/0087_ghaction_deployment_external_id_deployment_ref_and_more.py
# - comet/core/migrations/0094_deployment_deployer.py
# - comet/core/migrations/0118_secretmanager_secret.py
# - comet/core/migrations/0125_projectsettings_alter_deployment_status_and_more.py
# - comet/core/migrations/0125_promotiontemplate_promotiontemplatetotargets.py
# - comet/core/migrations/0134_alter_deployment_status_approvalrequest.py
# - comet/core/migrations/0135_approvalrequest_required_approvers.py
# - comet/core/migrations/0137_promotionrun_deployment_promotion.py
# - comet/core/migrations/0137_taskschedulerequest.py
# - comet/core/migrations/0140_infrastructuresettings_and_more.py
# - comet/core/migrations/0164_infratask_ciflakinesstask.py
# - comet/core/migrations/0168_documentationtask.py
# - comet/core/models/slack.py
AUTH_USER_MODEL=your_value_here

# - comet/core/sources/aws/aws.py
# - comet/core/storage/secrets.py
# - comet/core/utils/generic.py
# - comet/core/views/core_views.py
# - comet/settings/prod.py
# - comet/settings/staging.py
AWS_ACCESS_KEY_ID=your_value_here

# - comet/core/storage/secrets.py
AWS_REGION=your_value_here

# - comet/core/sources/aws/aws.py
# - comet/core/storage/secrets.py
# - comet/core/utils/generic.py
# - comet/core/views/core_views.py
# - comet/settings/prod.py
# - comet/settings/staging.py
AWS_SECRET_ACCESS_KEY=your_value_here

# - comet/core/utils/generic.py
BASE_DIR=your_value_here

# - comet/core/views/github.py
# - comet/core/views/slack.py
CALLBACK_BASE_URL=your_value_here

# - comet/api/api.py
# - comet/api/utils.py
# - comet/core/views/core_views.py
# - comet/settings/base.py
CASED_API_AUTH_API_KEY=your_value_here

# - comet/settings/prod.py
# - comet/settings/staging.py
CASED_INTERNAL_API_KEY=your_value_here

# - comet/settings/base.py
# - comet/tasks.py
CASED_INTERNAL_SLACK_URL=your_value_here

# - comet/settings/base.py
CASED_ORG_ID=your_value_here

# - comet/core/sources/aws/aws.py
# - comet/core/views/core_views.py
CASED_S3_BUCKET_NAME=your_value_here

# - comet/core/utils/generic.py
# - comet/core/utils/uri.py
# - comet/settings/development.py
CODESPACES=your_value_here

# - comet/settings/development.py
# - slack_socket.py
CODESPACE_NAME=your_value_here

# - comet/core/tasks/github_tasks.py
# - comet/settings/base.py
COMMIT_UPDATE_COMPUTATION_THRESHOLD=your_value_here

# - comet/core/management/commands/seed/secrets.py
# - comet/core/sources/datadog/datadog_source.py
DATADOG_API_KEY=your_value_here

# - comet/core/management/commands/seed/secrets.py
# - comet/core/sources/datadog/datadog_source.py
DATADOG_APP_KEY=your_value_here

# - comet/settings/local.py
DB_ENGINE=your_value_here

# - comet/api/api.py
# - comet/api/infrastructure.py
# - comet/celery.py
# - comet/core/logging.py
# - comet/core/middlewares/error_handler_middleware.py
# - comet/core/models/deployment.py
# - comet/core/models/project.py
# - comet/core/services/env_scanner_service.py
# - comet/core/services/litellm_service.py
# - comet/core/sources/datadog/datadog_source.py
# - comet/core/sources/github/async_github.py
# - comet/core/sources/github/github.py
# - comet/core/sources/sentry/sentry.py
# - comet/core/utils/generic.py
# - comet/core/views/core_views.py
# - comet/core/views/github.py
# - comet/core/views/slack.py
# - comet/settings/base.py
# - comet/tasks.py
# - comet/urls.py
DEBUG=your_value_here

# - comet/core/services/litellm_service.py
DEFAULT_LLM=your_value_here

# - comet/settings/base.py
DISABLE_DEPLOYMENTS_POLLING=your_value_here

# - comet/api/api.py
# - comet/settings/base.py
DISABLE_PRS_POLLING=your_value_here

# - comet/settings/development.py
# - comet/settings/prod.py
# - comet/settings/staging.py
DJANGO_SECRET_KEY=your_value_here

# - comet/asgi.py
# - comet/celery.py
# - comet/wsgi.py
DJANGO_SETTINGS_MODULE=your_value_here

# - comet/settings/base.py
ECS_CONTAINER_METADATA_URI=your_value_here

# - comet/core/storage/secrets.py
# - comet/core/utils/generic.py
# - comet/core/views/core_views.py
# - comet/tasks.py
ENV_NAME=your_value_here

# - comet/core/utils/generic.py
# - comet/core/utils/uri.py
FULL_CODESPACES_URI=your_value_here

# - comet/settings/development.py
GH_APP_ID=your_value_here

# - comet/core/utils/generic.py
# - comet/settings/base.py
# - comet/settings/local.py
# - comet/settings/prod.py
# - comet/settings/staging.py
GITHUB_APP_ID=your_value_here

# - comet/api/github_api.py
# - comet/core/views/core_views.py
# - comet/settings/local.py
# - comet/settings/prod.py
# - comet/settings/staging.py
GITHUB_APP_NAME=your_value_here

# - comet/core/utils/generic.py
# - comet/settings/local.py
# - comet/settings/prod.py
# - comet/settings/staging.py
GITHUB_APP_PRIVATE_KEY=your_value_here

# - comet/core/views/github.py
# - comet/settings/base.py
GITHUB_APP_SECRET=your_value_here

# - comet/core/views/github.py
# - comet/settings/local.py
# - comet/settings/prod.py
# - comet/settings/staging.py
GITHUB_CLIENT_ID=your_value_here

# - comet/core/views/github.py
GITHUB_CLIENT_SECRET=your_value_here

# - comet/settings/development.py
# - slack_socket.py
GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN=your_value_here

# - comet/core/sources/github/github.py
# - comet/settings/local.py
GITHUB_ORG_NAME=your_value_here

# - comet/core/sources/github/github.py
GITHUB_PAT=your_value_here

# - comet/settings/development.py
# - slack_socket.py
GITHUB_USER=your_value_here

# - comet/core/views/github.py
# - comet/settings/local.py
# - comet/settings/prod.py
# - comet/settings/staging.py
GITHUB_WEBHOOK_SECRET=your_value_here

# - comet/core/services/litellm_service.py
# - comet/settings/base.py
HELICONE_AUTH=your_value_here

# - comet/core/cortex/infra_agent.py
INFRA_RULES=your_value_here

# - comet/core/management/commands/seed/secrets.py
LINEAR_API_KEY=your_value_here

# - comet/core/management/commands/seed_data.py
LOAD_MOCK_DEPLOYMENTS=your_value_here

# - comet/celery.py
LOGGING=your_value_here

# - comet/settings/prod.py
# - comet/settings/staging.py
LOGTAIL_SOURCE_TOKEN=your_value_here

# - comet/core/logging.py
# - comet/settings/base.py
# - comet/settings/local.py
LOG_LEVEL=your_value_here

# - comet/core/services/email_service.py
# - comet/core/utils/generic.py
# - comet/settings/base.py
LOOPS_API_KEY=your_value_here

# - comet/settings/local.py
NGROK_HOST=your_value_here

# - .prettierrc.js
NODE_PATH=your_value_here

# - comet/core/plotter.py
OPENAI_API_BASE=your_value_here

# - comet/settings/base.py
OPENAI_API_KEY=your_value_here

# - comet/settings/prod.py
# - comet/settings/staging.py
OPENROUTER_KEY=your_value_here

# - comet/core/management/commands/seed/secrets.py
PAGERDUTY_API_KEY=your_value_here

# - comet/settings/base.py
PD_CHANNEL_ID=your_value_here

# - comet/settings/base.py
PD_TEAM_ID=your_value_here

# - comet/core/management/commands/seed/secrets.py
PINGDOM_API_KEY=your_value_here

# - comet/core/management/commands/seed/secrets.py
PLANETSCALE_SERVICE_TOKEN=your_value_here

# - comet/core/cortex/grapher.py
# - comet/core/cortex/post_actions.py
# - comet/core/plotter.py
# - comet/settings/base.py
PLOTTER_API_KEY=your_value_here

# - comet/core/cortex/grapher.py
# - comet/core/plotter.py
PLOTTER_BASE_URL=your_value_here

# - comet/settings/base.py
PROMETHEUS_DOMAIN=your_value_here

# - comet/settings/prod.py
# - comet/settings/staging.py
PSQL_HOST=your_value_here

# - comet/settings/prod.py
# - comet/settings/staging.py
PSQL_PASSWORD=your_value_here

# - comet/settings/prod.py
# - comet/settings/staging.py
PSQL_USER=your_value_here

# - comet/settings/base.py
REDIS_DB=your_value_here

# - comet/settings/base.py
REDIS_HOST=your_value_here

# - comet/settings/base.py
REDIS_PORT=your_value_here

# - comet/celery.py
# - comet/core/utils/generic.py
# - comet/settings/base.py
# - comet/settings/local.py
REDIS_URL=your_value_here

# - comet/core/models/deployment.py
# - comet/settings/local.py
RUN_DEPLOYS=your_value_here

# - comet/core/storage/secrets.py
SECRETS_FILE=your_value_here

# - comet/core/sources/source.py
# - comet/core/utils/generic.py
SECRETS_STORAGE_CLASS=your_value_here

# - comet/core/management/commands/seed/secrets.py
SEED_SECRETS=your_value_here

# - comet/core/management/commands/seed/secrets.py
# - comet/core/sources/sentry/sentry.py
# - comet/settings/base.py
SENTRY_AUTH_TOKEN=your_value_here

# - comet/settings/local.py
# - comet/settings/prod.py
# - comet/settings/staging.py
SENTRY_DSN=your_value_here

# - comet/core/services/litellm_service.py
# - comet/core/tasks/slack_tasks.py
# - comet/core/utils/generic.py
# - comet/core/utils/uri.py
# - comet/settings/base.py
SITE_URL=your_value_here

# - comet/settings/local.py
SLACK_APP_TOKEN=your_value_here

# - comet/settings/local.py
SLACK_BOT_TOKEN=your_value_here

# - comet/core/utils/generic.py
# - comet/core/views/core_views.py
# - comet/core/views/slack.py
# - comet/settings/local.py
# - comet/settings/prod.py
# - comet/settings/staging.py
# - comet/settings/test.py
SLACK_CLIENT_ID=your_value_here

# - comet/core/views/core_views.py
# - comet/core/views/slack.py
# - comet/settings/base.py
# - comet/settings/development.py
# - comet/settings/local.py
# - comet/settings/prod.py
# - comet/settings/staging.py
SLACK_CLIENT_SECRET=your_value_here

# - comet/core/views/core_views.py
SLACK_REDIRECT_URI=your_value_here

# - comet/core/chat/message_sender.py
# - comet/core/chat/slack_tasks.py
# - comet/core/utils/generic.py
# - comet/tasks.py
SLACK_SOCKET_CLIENT=your_value_here

# - comet/core/sources/source.py
STATIC_URL=your_value_here

# - comet/core/management/commands/seed/secrets.py
STATUSPAGE_API_KEY=your_value_here

# - comet/core/management/commands/seed/secrets.py
STATUSPAGE_PAGE_ID=your_value_here

# - comet/core/chat/slack_tasks.py
# - comet/core/models/slack.py
# - comet/core/utils/generic.py
STORAGE_KEY_OAUTH_SLACK=your_value_here

# - comet/core/chat/message_sender.py
# - comet/core/chat/slack_tasks.py
# - comet/core/utils/generic.py
# - comet/tasks.py
USE_SOCKET_CLIENT=your_value_here

# - comet/settings/base.py
VAULT_ADDR=your_value_here

# - comet/core/storage/secrets.py
# - comet/settings/base.py
VAULT_TOKEN=your_value_here

# - comet/core/storage/secrets.py
VAULT_URL=your_value_here
