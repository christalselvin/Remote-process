Overview
The Role Management API provides endpoints to manage roles, permissions, and role mappings within an application. It facilitates the creation, retrieval, updating, and deletion of roles, along with associating permissions and tabs to roles. The API ensures secure role-based access control (RBAC) for users.

Features
Role CRUD Operations: Create, retrieve, update, and delete roles.
Permission CRUD Operations: Manage permissions associated with roles.
Role Mapping: Map roles to specific permissions and tabs.
Role Validation: Validate role-related operations with session keys.
Error Handling: Handle exceptions and provide meaningful error messages.
Security: Secure endpoints with session keys for authorized access.
Technologies Used
Python
Flask framework
SQLAlchemy ORM for database operations
JWT (JSON Web Tokens) for session management
SQLite database (can be replaced with other databases like PostgreSQL, MySQL, etc.)
API Endpoints
Get All Tabs
Endpoint: /api/getAllTabs
Method: GET
Description: Retrieves all active tabs available in the system.
Get All Permissions
Endpoint: /api/getAllPermission
Method: GET
Description: Retrieves all active permissions defined in the system.
Create Role
Endpoint: /api/role/create
Method: POST
Description: Creates a new role in the system along with mappings to permissions and tabs.
Get All Roles
Endpoint: /api/role/getAllRoles
Method: GET
Description: Retrieves all roles available in the system.
Remove Role
Endpoint: /api/role/removeRole
Method: DELETE
Description: Deletes a specified role from the system if no users are associated with it.
Update Role
Endpoint: /api/role/updateRole
Method: PUT
Description: Updates an existing role's details and its associated permissions and tabs.
Get Roles Mappers
Endpoint: /api/role/getRolesMappers
Method: GET
Description: Retrieves mappings between roles, tabs, and permissions.
Get Role Mappers
Endpoint: /api/role/getRoleMappers
Method: GET
Description: Retrieves mappings of a specific role to its associated tabs and permissions.
Get One Role Mappers
Endpoint: /api/role/getOneRoleMappers
Method: GET
Description: Retrieves mappings of a specified role to its associated tabs and permissions if the role exists.
Installation
Clone the repository:
windows HTTPS
Copy code
git clone https://github.com/christalselvin/Remote-process.git
cd role-management-api
