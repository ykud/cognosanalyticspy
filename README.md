# cognosanalyticspy

Python wrappers for Cognos Analytics REST API

## Overview

This is a collection of Python wrapper methods for:

1. [Cognos Analytics REST API calls](https://www.ibm.com/docs/en/cognos-analytics/12.0.0?topic=api-rest-reference)
2. [Cognos Mashup Services REST API](https://www.ibm.com/docs/en/cognos-analytics/11.1.0?topic=guide-overview-mashup-service) calls to execute reports (just very basic)
3. An example of how to use the 'unoffical' APIs like `/namespaces` calls to list groups & roles in namespace_folders

The goal is to be able to run code like this against your Cognos Analytics environment:

``` python
ca_service = CognosAnalyticsService(ca_url='https://your_cognos_dispatcher:9300')
# Login
ca_service.login(namespace='namespace',user='user',password='pwd')
# get list of content items from team folders
team_folders_items = ca_service.content.get_content_items(content_id='team_folders')
print(team_folders_items)
```

See [samples.py](samples.py) for more examples of different services calls.

This code is inspired by [tm1py](https://github.com/cubewise-code/tm1py), but is nowhere near as polished or tested, feel free to improve and expand. I'm releasing this as I might not have a chance to work on this in near future.

Please see the [blog post for some background of how I've used this](https://ykud.com/blog/ca-rest-api-python).

## Structure

[objects](/objects/) folder contains `data classes` for various Cognos Analytics objects (users, groups, content items, etc)
[services](/services/) folder contains the wrappers for different endpoints for restapi, namely:

* [cognos_analytics](services/cognos_analytics.py) - main service that exposes all the other services
* [content](services/content.py) - content related methods, e.g. reading contents of a folder, updating permissions of a report
* [groups](services/groups.py) & [roles](services/roles.py) - groups & roles related methods, adding / removing groups or members
* [namespaces](services/namespaces.py) - an 'unofficial' method for querying members of `namespace_folders` - an example of how methods used by Cognos Analytics UI can be included
* [report_data](services/report_data.py) - Cognos Mashup Services wrapper to run the reports and return data
* [rest](services/rest.py) - a wrapper around requests library for executing HTTP calls
* [users](services/users.py) - adding / removing users from namespace and copying user profiles and settings
