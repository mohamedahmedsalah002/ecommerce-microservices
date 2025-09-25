// MongoDB initialization script
db = db.getSiblingDB('ecommerce_users');

// Create users collection with indexes
db.createCollection('users');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "created_at": 1 });
db.users.createIndex({ "is_active": 1 });

print('Database initialized successfully!');
