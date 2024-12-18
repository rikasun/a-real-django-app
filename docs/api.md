
## Overview

This API provides endpoints for managing projects. All responses are in JSON format.

## Authentication

Currently, the API does not require authentication. This will be added in future versions.

## Endpoints

### Projects

#### List Projects

```
GET /api/projects/
```

Returns a list of all projects.

**Response**
```json
[
    {
        "id": 1,
        "name": "Project Name",
        "description": "Project Description",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

#### Create Project

```
POST /api/projects/
```

Create a new project.

**Request Body**
```json
{
    "name": "New Project",
    "description": "Project Description"
}
```

**Response**
```json
{
    "id": 1,
    "name": "New Project",
    "description": "Project Description",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Get Project

```
GET /api/projects/{id}/
```

Get a specific project by ID.

**Response**
```json
{
    "id": 1,
    "name": "Project Name",
    "description": "Project Description",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Update Project

```
PUT /api/projects/{id}/
```

Update a specific project.

**Request Body**
```json
{
    "name": "Updated Name",
    "description": "Updated Description"
}
```

#### Delete Project

```
DELETE /api/projects/{id}/
```

Delete a specific project.

## Error Handling

The API uses standard HTTP response codes:

- 200: Success
- 201: Created
- 204: No Content
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

Error responses include a message describing the error:

```json
{
    "error": "Error message here"
}
```

## Rate Limiting

Currently, there are no rate limits implemented. This will be added in future versions.

## Changelog

### Version 1.0.0
- Initial API release
- Basic CRUD operations for Projects