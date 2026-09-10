# Agent Guidelines for AI-Daily Project

## File Output and Path Standards

1. **Workspace Output Priority**:
   - All generated daily briefs (daily-brief-YYYY-MM-DD.md) and HTML newspaper layouts (-brief-*.html, m-brief-*.html) must always be saved or synchronized directly to the project workspace output directory: output/ (i.e. d:/Users/Alex/AI-Daily/output/).
   - The user monitors this repository in their editor; saving only to ~/.claude/ hides files inside a dot-folder that is invisible in the project file explorer.

2. **Windows Path Formatting & Clickable Links**:
   - **Never** output bare tilde (~) paths to the user (e.g. ~/.claude/...). Windows Explorer, PowerShell, and run dialogs do not consistently resolve ~.
   - Always provide **clickable links** using the ile:/// URI scheme with forward slashes:
     e.g., [daily-brief-YYYY-MM-DD.md](file:///d:/Users/Alex/AI-Daily/output/daily-brief-YYYY-MM-DD.md)
   - Show both the workspace relative path (output/daily-brief-YYYY-MM-DD.md) and the resolved absolute path.

3. **Opening Files on Windows**:
   - When opening generated files programmatically, target the workspace file path and use Invoke-Item or Start-Process code ....
