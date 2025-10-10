import React from 'react';
import LoadingSpinner from '../../src/components/LoadingSpinner';
import { useAuth } from '../../src/contexts/AuthContext';

const Profile: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
            <div className="mt-6 space-y-4">
              <div>
                <div className="text-sm text-gray-500">Name</div>
                <div className="text-gray-900">{user.name}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Email</div>
                <div className="text-gray-900">{user.email}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;



