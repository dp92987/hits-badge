#!/bin/bash

URL=https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage
AUTHOR_NAME=$(git log -1 $TRAVIS_COMMIT --pretty="%aN")

if [ $TRAVIS_TEST_RESULT -ne 0 ]; then
  BUILD_STATUS=FAILED
else
  BUILD_STATUS=OK
fi

if [ $1 -eq 1 ]; then
  DEPLOY_STATUS=FAILED
elif [ $1 -eq -1 ]; then
  DEPLOY_STATUS=N/A
else
  DEPLOY_STATUS=OK
fi

MSG="$TRAVIS_REPO_SLUG build <a href=\"$TRAVIS_BUILD_WEB_URL\">#$TRAVIS_BUILD_NUMBER</a>:

<pre>repository: $TRAVIS_REPO_SLUG
branch: $TRAVIS_BRANCH
commit: $(echo $TRAVIS_COMMIT | head -c 7)
message: $TRAVIS_COMMIT_MESSAGE
author: $AUTHOR_NAME

build: $BUILD_STATUS
deploy: $DEPLOY_STATUS</pre>"

curl -s -X POST $URL -d chat_id=$TELEGRAM_CHAT_ID -d text="$MSG" -d parse_mode="HTML" -d disable_web_page_preview=1 > /dev/null
