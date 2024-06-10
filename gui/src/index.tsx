import React from 'react';
import { createRoot } from 'react-dom/client';
import { Helmet } from 'react-helmet';

import App from './App';

import { APP_TITLE, APP_DESCRIPTION } from './utils/constants';

// Find the root element
const rootElement = document.getElementById('root');


if (rootElement) {
  // Create a root
  const root = createRoot(rootElement);

  // Render the app
  root.render(
    <React.StrictMode>
      <Helmet>
        <title>{APP_TITLE}</title>
        <meta name="description" content={APP_DESCRIPTION} />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
        />
        <meta name="viewport" content="initial-scale=1, width=device-width" />
      </Helmet>
      <App />
    </React.StrictMode>
  );
}
