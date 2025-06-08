# Your operating environment
- You are running on Windows
- Use ; separator when you need to execute multiple commands
- Use Windows PowerShell commands

# Styling and formatting
When doing styles, always use dark themed styles
When choosing colors, ooking for colors that exude grandeur, prestige, and nobility—a regal palette! In higher-level terms, these shades fall under the category of “imperial” or “majestic” colors, often associated with royalty, power, and luxury, such as Imperial Purple, Royal Blue and others. Select shades from the Pantone Matching System (PMS) that align with the richness and elegance of imperial hues.
When working with date and time, always use European date and time formatting

# Testing
Always write tests, and to validate functionality execute tests, only after tests are successful try running the application to validate additional functionality.

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