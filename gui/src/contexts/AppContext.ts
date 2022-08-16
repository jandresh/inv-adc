import React, { createContext } from 'react';

import { User } from '../types';

export interface IAppContext {
  user: User;
  setUser: React.Dispatch<React.SetStateAction<User>>;
}

export const AppContext = createContext<IAppContext>({
  user: {
    id: '',
    firstName: 'guest',
    lastName: '',
    email: '',
    createdAt: new Date(),
    updatedAt: new Date(),
    isActive: false,
    isAdmin: false,
    isVerified: false
  },
  setUser: () => {}
});
