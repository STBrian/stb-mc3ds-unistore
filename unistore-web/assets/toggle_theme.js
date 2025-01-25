const currentTheme = localStorage.getItem("theme");
if (currentTheme == "light") {
  document.body.classList.add("light-theme");
}
else
{
  document.body.classList.add("dark-theme");
}

async function toggle_theme() {
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
  let defaultDark = prefersDarkScheme.matches;
  let theme = "dark";
  if (!document.body.classList.contains("light-theme") && !document.body.classList.contains("dark-theme")) {
    if (!defaultDark) {
      theme = "light";
      document.body.classList.add("light-theme");
    }
    else {
      document.body.classList.add("dark-theme");
    }
  }
  else {
    document.body.classList.toggle("light-theme");
    document.body.classList.toggle("dark-theme");
    if (document.body.classList.contains("light-theme")) {
      theme = "light";
    }
    else if (document.body.classList.contains("dark-theme")) {
      theme = "dark";
    }
  }

  localStorage.setItem("theme", theme);
}