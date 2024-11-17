import React, { useEffect, useMemo, useState } from 'react';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import { Layout } from './components/Layout';
import { PageDefault } from './components/PageDefault';

import { AppContext, ThemeModeContext } from './contexts';
import routes from './config/routes';
import { Route as AppRoute, User } from './types';

import { getAppTheme } from './styles/theme';
import { DARK_MODE_THEME, LIGHT_MODE_THEME } from './utils/constants';
import { NotFound } from 'components/Navigation/Routes/NotFound';
import { guestUser } from 'contexts/AppContext';

function App () {
  const [mode, setMode] = useState<
    typeof LIGHT_MODE_THEME | typeof DARK_MODE_THEME
  >(LIGHT_MODE_THEME);

  const themeMode = useMemo(() => ({
    toggleThemeMode: () => {
      setMode(prevMode => prevMode === LIGHT_MODE_THEME ? DARK_MODE_THEME : LIGHT_MODE_THEME);
    }
  }), []);

  const theme = useMemo(() => getAppTheme(mode), [mode]);

  const [user, setUser] = useState<User>({
    id: '',
    orgId: '',
    firstName: 'guest',
    lastName: '',
    email: '',
    createdAt: new Date(),
    updatedAt: new Date(),
    isActive: false,
    isAdmin: false,
    isVerified: false,
    role: 'guest'
  });

  const appClient = { user, setUser };

  const addRoute = (route: AppRoute) => (
    <Route
      key={route.key}
      path={route.path}
      element={
        <React.Fragment>
          {route.component ? <route.component /> : <PageDefault />}
        </React.Fragment>}
    />
  );

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    } else {setUser(guestUser)}
  }, []);

  return (
    <AppContext.Provider value={appClient}>
      <ThemeModeContext.Provider value={themeMode}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Router>
            <Layout>
              <Routes>
                {routes.filter(
                  (route) => route.allowedRoles.includes(user.role)
                ).map((route: AppRoute) =>
                  route.subRoutes
                    ? route.subRoutes.filter(
                      (subRoute) => subRoute.allowedRoles.includes(user.role)
                    ).map((item: AppRoute) => addRoute(item))
                    : addRoute(route)
                )}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Layout>
          </Router>
        </ThemeProvider>
      </ThemeModeContext.Provider>
    </AppContext.Provider>
  );
}

export default App;
