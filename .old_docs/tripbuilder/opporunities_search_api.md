# Opportunities Search API

Please note: Due to the complexity of the advanced filtering requirements, updates may take a few seconds to appear in the search results.

The Opportunities Search API enables users to search for opportunities within your CRM system based on specified criteria. It offers extensive filtering, sorting, and pagination options to refine search results according to specific needs.
### 📌 Endpoint
`POST /opportunities/search`
* * *
## 🔸 Request Body

| **Parameter** | **Type** | **Required** | **Description** | **Limit** |
| ---| ---| ---| ---| --- |
| `locationId` | string | Yes | Location ID in which the search needs to be performed. | NA |
| `page` | number | No | The page number of results to retrieve. Used for standard pagination.<br>⚠️ **Note**: _When using_ _`searchAfter`_ _parameter,_ _`page`_ _should not be provided._ | **_min_**: 0 |
|  |
| `limit` | number | Yes | The number of results to limit per page. | **_min_**: 1, **_max_**: 500 |
| `searchAfter` | array | No | Used for cursor-based pagination. This value is returned in the response and defines start point.<br>⚠️ **Note**: _Required for retrieving results beyond 10,000 records._ | NA |
|  |
| `query` | string | No | The string you want to search for within your opportunities. The results will depend on the searchable fields you’ve configured.<br>For more information on how searchable fields work for opportunities, please refer to this guide:<br>[https://help.gohighlevel.com/support/solutions/articles/155000003913-searching-an-object-record](https://help.gohighlevel.com/support/solutions/articles/155000003913-searching-an-object-record)<br><br> | **_max_**_: 75 Character_ |
| `filters` | array | No | Array of filters or nested filter groups to refine search results. | NA |
| `sort` | array | No | Array of sorting criteria to apply for ordering search results. | NA |
| `additionalDetails` | object | No | Request additional related data. | NA |
| ├── `notes` | boolean | No | Include notes (`true` or `false`) | NA |
| ├── `tasks` | boolean | No | Include tasks (`true` or `false`) | NA |
| └── `calendarEvents` | boolean | No | Include calendar events (`true` or `false`) | NA |

* * *
## 🔄 Pagination Limitations
### Standard Pagination (`page` & `limit`)
*   Can fetch a maximum of 10,000 records in total.
*   Use `page` and `limit` parameters.
### Cursor-based Pagination (`searchAfter` & `limit`)
*   Required for accessing more than 10,000 records.
*   Use the `searchAfter` parameter returned in each response to fetch the next set of results.
*   Do **not** include the `page` parameter when using `searchAfter`.
*   Allows for efficient pagination through large result sets.
* * *
## 📥 Sample Request Body

```json
{
  "locationId": "5DP41231LkQsiKESj6rh",
  "page": 1,
  "limit": 20,
  "searchAfter": [
    "bs5qhs78vqhs",
    "2FP41231LkQsiKESj6eg"
  ],
  "query": "john@example.com",
  "filters": [
    {
      "field": "status",
      "operator": "eq",
      "value": "open"
    },
    {
      "group": "OR",
      "filters": [
        {
          "field": "pipeline_id",
          "operator": "eq",
          "value": "bCkKGpDsyPP4peuKowkG"
        },
        {
          "field": "pipeline_stage_id",
          "operator": "eq",
          "value": "7915dedc-8f18-44d5-8bc3-77c04e994a10"
        }
      ]
    }
  ],
  "sort": [
    {
      "field": "date_added",
      "direction": "desc"
    }
  ],
  "additionalDetails": {
    "notes": true,
    "tasks": true,
    "calendarEvents": false
  }
}
```

* * *
## 🔍 Filters
The Opportunities Search API supports a variety of filters that allow users to refine their search results based on specific criteria. Filters can be applied individually or grouped together using logical operators (AND, OR) to create complex search queries, each comprising three essential components:
*   **Field**: Indicates the attribute or property of opportunities by which the filter is applied.
*   **Operator**: Specifies the operation to be performed on the field to filter opportunities.
*   **Value**: Represents the specific value against which the field is compared.
* * *
### 🧪 Sample Filter Payload

```json
{
  "group": "AND",
  "filters": [
    {
      "group": "AND",
      "filters": [
        {
          "field": "status",
          "operator": "eq",
          "value": "open"
        },
        {
          "field": "monetary_value",
          "operator": "range",
          "value": {
            "gte": 1000,
            "lte": 5000
          }
        }
      ]
    },
    {
      "group": "OR",
      "filters": [
        {
          "field": "assigned_to",
          "operator": "eq",
          "value": "082goXVW3lIExEQPOnd3"
        },
        {
          "field": "source",
          "operator": "exists"
        }
      ]
    }
  ]
}
```

* * *
### ✅ Supported Filter Operators

| **Operator** | **Definition** | **Value Type** | **Example** | **Character**<br>**Limit** |
| ---| ---| ---| ---| --- |
| `eq` | Equals | Number, String, Boolean | ![](https://t8631005.p.clickup-attachments.com/t8631005/abd71667-d3b2-4a54-a60d-65801e95c734/image.png) | None |
| `not_eq` | Not Equals | Number, String, Boolean | ![](https://t8631005.p.clickup-attachments.com/t8631005/4d9ad077-d52a-44ae-a5e2-d575bfe8ef23/image.png) | None |
| `contains` | Contains | String `(The contains operator does not support special characters.)` | ![](https://t8631005.p.clickup-attachments.com/t8631005/1b7a95b8-ca1d-4e22-add6-b5404a740b38/image.png) | 75 |
| `not_contains` | Not Contains | String `(The not_contains operator does not support special characters.)` | ![](https://t8631005.p.clickup-attachments.com/t8631005/3e9c7b9f-05f5-41b7-8070-19161f5f9d58/image.png) | 75 |
| `exists` | Exists (has a value) | Undefined `(Do not pass any value, just field and operator are enough)` | ![](https://t8631005.p.clickup-attachments.com/t8631005/ecf8d898-b878-417a-807a-7f73d8348a0e/image.png) | None |
| `not_exists` | Does not exist (no value) | Undefined `(Do not pass any value, just field and operator are enough)` | ![](https://t8631005.p.clickup-attachments.com/t8631005/32ceb277-c62b-4c82-925a-bcd9bf01b2ca/image.png) | None |
| `range` | Range | Object with `gte`, `lte`, `gt`, `lt`<br><br>![](https://t8631005.p.clickup-attachments.com/t8631005/300cc05b-9b1d-4193-98a4-b4c1ab611d2c/image.png) | ![](https://t8631005.p.clickup-attachments.com/t8631005/b66d6770-fe91-4e32-bcc3-09471d06a2ee/image.png) | 75 |

* * *
### 📚 Supported Filter Fields

| **Display Name** | **Field Name** | **Supported Operators** | **Example** |
| ---| ---| ---| --- |
| **OPPORTUNITY INFORMATION** |
| Opportunity ID | `id` | eq, not\_eq | ![](https://t8631005.p.clickup-attachments.com/t8631005/a33fa007-2db9-42af-bbc0-5cd1f1e3a541/image.png) |
| Opportunity Name | `name` | eq, not\_eq, contains, not\_contains, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/c3d50a5f-0c0c-49d5-9b89-e04abfda086e/image.png) |
| Monetary Value | `monetary_value` | eq, not\_eq, range, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/9b7841aa-d90f-4f9e-bba6-e43c29412cdf/image.png) |
| Pipeline ID | `pipeline_id` | eq, not\_eq, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/bdadf746-0cf4-4169-80f8-066173a4566b/image.png) |
| Pipeline Stage ID | `pipeline_stage_id` | eq, not\_eq, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/55f82117-d4a7-44ca-bc76-e979fc2db6ce/image.png) |
| Status | `status` | eq, not\_eq, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/3e28abcc-6076-4304-8470-fa47fc6a5490/image.png) |
| Lost Reason ID | `lost_reason_id` | eq, not\_eq, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/493c586a-89b6-41a3-adc6-447b5a3be2e4/image.png) |
| Source | `source` | eq, not\_eq, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/a07120fb-1da3-4a02-ac7f-3d95d0d1dd47/image.png) |
| Assigned To | `assigned_to` | eq, not\_eq, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/86bf8756-050b-4475-81cb-ddb142b28ddc/image.png) |
| Followers | `followers` | eq, not\_eq, contains, not\_contains, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/907059ad-a2ec-4834-85b4-544e2a5e911e/image.png) |
| **CONTACT INFORMATION** |
| Contact ID | `contact_id` | eq, not\_eq, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/6bd79e26-2b36-436a-9b34-56c462614dc7/image.png) |
| Contact Name | `contact_name` | eq, not\_eq, contains, not\_contains, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/c2d65f37-3afb-4f48-9bb1-637ebf36bffe/image.png) |
| Company Name | `company_name` | eq, not\_eq, contains, not\_contains, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/ae92fe78-44fb-4194-b676-974240b2cbf7/image.png) |
| Email | `email` | eq, not\_eq, contains, not\_contains, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/c4369d6d-f7fe-405b-836a-b2526e21cfc5/image.png) |
| Phone | `phone` | eq, not\_eq, contains, not\_contains, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/980916be-2199-413f-8264-a0ad8113cd3f/image.png) |
| **DATE FIELDS** |
| Date Added | `date_added` | range, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/665e463d-6958-418c-8911-ec032127fa2e/image.png) |
| Date Updated | `date_updated` | range, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/66f05ef3-bd09-415d-90c6-e4d68ae92e59/image.png) |
| Last Status Change Date | `last_status_change_date` | range, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/b2fc5822-f0d5-476b-9640-89fbde413eb8/image.png) |
| Last Stage Change Date | `last_stage_change_date` | range, exists, not\_exists | ![](https://t8631005.p.clickup-attachments.com/t8631005/1a5b4b5b-4b4d-46e2-8f26-76878a04d9d3/image.png) |
| **CUSTOM FIELDS** |
| _TEXT_<br><br>_LARGE\_TEXT_<br><br>_SINGLE\_OPTIONS_<br><br>_RADIO_<br><br>_PHONE_<br><br> | _`custom_fields`_`.`_`{{ custom_field_id }}`_<br>Eg: _`custom_fields`_`.OBj007JIEmLP0IEHdV1l`<br><br> | eq<br>not\_eq<br>contains<br>not\_contains<br>exists<br>not\_exists<br> | <br><br>![](https://t8631005.p.clickup-attachments.com/t8631005/f57d94fb-556a-4e27-93a9-540cb7cb7765/image.png)<br>![](https://t8631005.p.clickup-attachments.com/t8631005/f6ff9030-68d1-4f96-a9f4-e84f48949ffc/image.png) |
| _CHECKBOX_<br><br>_MULTIPLE\_OPTIONS_<br><br> | eq<br>not\_eq<br>exists<br>not\_exists<br> | ![](https://t8631005.p.clickup-attachments.com/t8631005/c7d9b445-810b-4bf4-83df-09c1d6e8b729/image.png)<br>![](https://t8631005.p.clickup-attachments.com/t8631005/56de0f21-e3ef-45a1-8dec-ceb8d0deeb4d/image.png) |
| _NUMERICAL_<br><br>_MONETORY_<br><br> | range<br>exists<br>not\_exists<br>eq<br>not\_eq<br> | ![](https://t8631005.p.clickup-attachments.com/t8631005/5a371ee5-322a-4fc6-94f2-e1d53a181e85/image.png)<br>![](https://t8631005.p.clickup-attachments.com/t8631005/13843a95-9d2b-4023-be69-ef2a58411e50/image.png) |
| _DATE_<br><br> | range<br>exists<br>not\_exists<br> | ![](https://t8631005.p.clickup-attachments.com/t8631005/98e9f9b2-34c8-42d8-abec-a3c3932754cf/image.png)<br><br>![](https://t8631005.p.clickup-attachments.com/t8631005/9959eb7d-d209-46ce-9236-60c833417878/image.png) |
| _TEXTBOX\_LIST_<br><br> | `custom_fields.`_`{{ custom_field_id }}.{{ optionoption_id }}`_<br>Eg: `custom_fields.OBj007JIEmLP0IEHdV1l.c1b70ec9-664f-400f-a3fc-6f7912c5e310`<br> | eq<br>not\_eq<br>contains<br>not\_contains<br>exists<br>not\_exists<br> | ![](https://t8631005.p.clickup-attachments.com/t8631005/dee8eecc-b30e-4c61-a593-c4921d2476c7/image.png) |

* * *
## ↕️ Sort
The Opportunities Search API supports sorting based on various fields. Users can specify:
*   **Field**: Attribute of opportunity to sort by.
*   **Direction**: "asc" (ascending) or "desc" (descending)
### ✅ Sample Sort Payload

```json
[
  {
  "field": "date_added",
  "direction": "desc"
  },
  {
   "field": "monetary_value",
   "direction": "asc"
  }
]
```

* * *
### 🔢 Supported Sort Fields

| **Display Name** | **Field Name** | **Example** |
| ---| ---| --- |
| Date Created | `date_added` | ![](https://t8631005.p.clickup-attachments.com/t8631005/728d46f9-a7bd-412f-bb1b-16084132cdf8/image.png) |
| Date Updated | `date_updated` | ![](https://t8631005.p.clickup-attachments.com/t8631005/a2c0b546-c6c4-461b-be85-65a53be6b59f/image.png) |
| Opportunity Name | `name` | ![](https://t8631005.p.clickup-attachments.com/t8631005/f0606659-0b8f-4d2e-90ca-ff5ec0805882/image.png) |
| Monetary Value | `monetary_value` | ![](https://t8631005.p.clickup-attachments.com/t8631005/225f7fb4-f427-4bb1-bb90-fdff704fec5d/image.png) |
| Last Status Change Date | `last_status_change_date` | ![](https://t8631005.p.clickup-attachments.com/t8631005/d941b8cf-a8ee-4225-8cb8-36176d887b63/image.png) |
| Last Stage Change Date | `last_stage_change_date` | ![](https://t8631005.p.clickup-attachments.com/t8631005/252ac511-dcf3-477e-b659-faa32c5dc635/image.png) |

* * *
## 📤 Response Body

```json
{
  "opportunities": [
    {
      "id": "yWQobCRIhRguQtD2llvk",
      "name": "New Business Opportunity",
      "monetaryValue": 5000,
      "pipelineId": "VDm7RPYC2GLUvdpKmBfC",
      "pipelineStageId": "e93ba61a-53b3-45e7-985a-c7732dbcdb69",
      "assignedTo": "zT46WSCPbudrq4zhWMk6",
      "status": "open",
      "source": "Website",
      "lastStatusChangeAt": "2024-06-06T18:54:57.221Z",
      "lastStageChangeAt": "2024-06-06T18:54:57.221Z",
      "lastActionDate": "2024-06-06T18:54:57.221Z",
      "createdAt": "2024-06-06T18:54:57.221Z",
      "updatedAt": "2024-06-06T18:54:57.221Z",
      "contactId": "zT46WSCPbudrq4zhWMk6",
      "locationId": "zT46WSCPbudrq4zhW",
      "contact": {
        "id": "byMEV0NQinDhq8ZfiOi2",
        "name": "John Doe",
        "companyName": "Tesla Inc",
        "email": "john@example.com",
        "phone": "+1202-555-0107",
        "tags": [
          "vip",
          "prospect"
        ]
      },
      "relations": [
        {
          "associationId": "OPPORTUNITIES_CONTACTS_ASSOCIATION",
          "relationId": "xb62wMnB0pBtR5Xl6ywn",
          "primary": true,
          "objectKey": "contact",
          "recordId": "YHZUIvl71fpcKr67aYEf",
          "fullName": "jnjnjn",
          "contactName": "jnjnjn",
          "companyName": null,
          "email": null,
          "phone": null,
          "tags": [],
          "attributed": null
        }
      ],
      "lostReasonId": null,
      "custom_fields": [
        {
          "id": "MgobCB14YMVKuE4Ka8p1",
          "fieldValue": "High Priority"
        },
        {
          "id": "qweqgehuqwejqeiqwoqw",
          "fieldValue": [
            "option-1",
            "option-2"
          ]
        }
      ],
      "followers": [
        "682goXVW3lIExEQPOnd3",
        "582goXVW3lIExEQPOnd3"
      ],
      "notes": [],
      "tasks": [],
      "calendarEvents": []
    }
  ],
  "total": 120,
  "aggregations": {}
}
```