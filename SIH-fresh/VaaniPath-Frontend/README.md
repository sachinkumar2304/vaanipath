# Project VanniPath

This project is a learning management system.

## Getting Started

To run the project locally:

```sh
npm install
npm run dev
```

## Features

- **Rapid Development**: Built with Vite for fast development.
- **UI Components**: Uses Shadcn UI for beautiful, accessible components.
- **Styling**: Tailwind CSS for utility-first styling.
- **Icons**: Lucide React for crisp, clean icons.

## Development

This project is a single page application (SPA) built with React and Vite.

To modify the page, find the `src/pages/Index.tsx` file and begin editing.

**Add a new page**

To add a new page, create a new file in `src/pages/` (e.g., `About.tsx`) and add a route in `src/App.tsx`.

```tsx
import About from "./pages/About";

<Route path="/about" element={<About />} />
```

**Add a custom component**

To add a custom component, create a new file in `src/components/` (e.g., `MyComponent.tsx`) and import it in your page.

```tsx
import MyComponent from "./components/MyComponent";

const Index = () => {
  return (
    <div>
      <MyComponent />
    </div>
  );
};
```
