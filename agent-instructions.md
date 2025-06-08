# Your operating environment
- You are running on Windows
- You are already in current project directory
- Use ; separator when you need to execute multiple commands
- Use Windows PowerShell commands

# Python Packages
- Never specify exact version of python packages, use latest

# Formatting
When working with date and time, always use European date and time formatting

# Color Usage Guidelines
When doing styles, always use dark themed style
When choosing colors, looking for colors that exude grandeur, prestige, and nobility—a regal palette! 
In higher-level terms, these shades fall under the category of “imperial” or “majestic” colors, often associated with royalty, power, and luxury, such as Imperial Purple, Royal Blue and others. 
Select shades from the Pantone Matching System (PMS) that align with the richness and elegance of imperial hues.

## **1. Color Harmony Principles**
To achieve a **cohesive and visually pleasing** design, follow these principles:
- **Analogous Colors** – Use colors that sit next to each other on the color wheel for a smooth transition.
- **Monochromatic Shades** – Maintain consistency by using variations of a single color.
- **Limited Palette** – Stick to **3-5 core colors** to avoid excessive contrast.
- **Soft Contrast** – Avoid sharp transitions; use intermediate shades for blending.

## **2. Establishing a Hierarchy**
Define colors based on their function:
- **Primary Color** – The dominant theme color (e.g., Dark Purple #4B0082).
- **Secondary Colors** – Supportive accents that blend well (e.g., Deep Maroon #800020, Navy #1E1B45).
- **Neutral Colors** – Background and text colors ensuring readability (e.g., Black #000000, Dark Gray #333333, Soft Lavender #A88EBC).
- **Accent Colors** – Carefully selected pops of color for highlights (e.g., Metallic Silver #C0C0C0).

## **3. Forbidden Color Pairings**
To prevent excessive contrast or visual strain:
- **Avoid high saturation clashes**, such as **yellow-green next to deep purple**.
- **Do not mix warm and cool tones** aggressively (e.g., bright red against cold blue).
- **Avoid neon colors** in a dark-themed design.
- **Ensure background and text contrast is subtle yet readable** (e.g., use off-white instead of pure white).

## **4. Recommended Contrast Levels**
- **Text-to-Background Ratio** – Minimum **4.5:1 contrast** for readability.
- **Button & UI Elements** – Ensure distinguishable hover effects without harsh color transitions.
- **Gradient Usage** – Use **soft tonal shifts** instead of sharp edges.

## **5. Implementation Tips**
- Use **color palettes** in design software (Figma, Photoshop) with pre-set schemes.
- Define **global color variables** in code (`theme-primary`, `theme-secondary`).
- Conduct **regular design reviews** to maintain color consistency.

# Testing
- It is imperative you always write tests, for both backend and front end
- To validate functionality execute tests, only after tests are successful try running the application to validate additional functionality.

# Development Guidelines
## **Follow SOLID Principles**
1. **Single Responsibility Principle (SRP)**  
   - A class should have only **one reason to change**, meaning it should have a single responsibility.
2. **Open-Closed Principle (OCP)**  
   - Software entities (classes, modules, functions) should be **open for extension but closed for modification**.
3. **Liskov Substitution Principle (LSP)**  
   - Subtypes must be **substitutable** for their base types without altering the correctness of the program.
4. **Interface Segregation Principle (ISP)**  
   - Clients should not be forced to depend on **interfaces they do not use**; instead, interfaces should be **small and specific**.
5. **Dependency Inversion Principle (DIP)**  
   - High-level modules should not depend on low-level modules; both should depend on **abstractions**.
## **Enforce These Best Practices**
### **1. Modular Programming**
- Break software into **independent modules** that handle specific functionalities.
- Modules should have **high cohesion** (everything inside is closely related) and **loose coupling** (minimal dependencies between modules).
### **2. Separation of Concerns (SoC)**
- Each file should **focus on a single responsibility**, preventing unnecessary complexity.
- Helps maintain **clarity and reusability** by keeping UI, logic, and data handling distinct.
### **3. Encapsulation**
- Each file should **contain only what it needs** to function, hiding unnecessary details from other parts of the system.
- Improves **security, maintainability, and modularity**.
### **4. Single Responsibility Principle (SRP)**
- Files and classes should have **one reason to change**, avoiding bloated structures.
- Prevents files from handling **multiple tasks**, ensuring clear separation.
### **5. File Structure Best Practices**
- **Organize files logically** based on their function:
  ```
  ├── src/
  │   ├── components/
  │   ├── services/
  │   ├── models/
  │   ├── utils/
  │   ├── config/
  │   ├── tests/
  ```
- **Use clear and consistent naming conventions** to improve readability.
- **Avoid deep nesting**, keeping hierarchy simple and manageable.
## **Additional Considerations**
### **Feature-Based Folder Structure**
- Consider **grouping files by feature** rather than type:
  ```
  ├── authentication/
  │   ├── login.js
  │   ├── register.js
  │   ├── authService.js
  ├── dashboard/
  │   ├── dashboardView.js
  │   ├── dashboardService.js
  │   ├── dashboardStyles.css
  ```
### **Consistent Naming**
- Follow **consistent casing** throughout the project (`camelCase`, `PascalCase`, `snake_case`).
- Ensure filenames are **descriptive yet concise**.