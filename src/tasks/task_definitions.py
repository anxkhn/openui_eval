"""
Task definitions for the multimodal LLM benchmark system.
This module contains predefined tasks for evaluating HTML generation capabilities
across different complexity levels and use cases.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class TaskCategory(Enum):
    """Categories for organizing tasks."""

    CALCULATOR = "calculator"
    WEBSITE = "website"
    PORTFOLIO = "portfolio"
    DASHBOARD = "dashboard"
    GAME = "game"
    FORM = "form"
    VISUALIZATION = "visualization"
    INTERACTIVE = "interactive"


class DifficultyLevel(Enum):
    """Difficulty levels for tasks."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class TaskDefinition:
    """Definition of a benchmark task."""

    name: str
    category: TaskCategory
    difficulty: DifficultyLevel
    prompt: str
    description: str
    requirements: List[str]
    evaluation_criteria: List[str]
    expected_features: List[str]
    time_estimate_minutes: int
    tags: List[str]


# Predefined tasks for the benchmark system
PREDEFINED_TASKS: Dict[str, TaskDefinition] = {
    # Calculator Tasks
    "basic_calculator": TaskDefinition(
        name="basic_calculator",
        category=TaskCategory.CALCULATOR,
        difficulty=DifficultyLevel.BEGINNER,
        prompt="""Create a sophisticated, responsive calculator with modern UI design.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a sleek, modern calculator interface with a dark theme using gradients of charcoal and deep blue.
- Include all basic arithmetic operations (+, -, *, /), number buttons (0-9), decimal point, equals, and clear/all-clear buttons.
- The display should be large and clearly readable with a subtle inner shadow effect.
- Buttons should have hover effects with subtle color transitions and a pressed state animation.
- Implement proper calculation logic with error handling for division by zero and invalid operations.
- The calculator should be fully responsive, adapting beautifully from mobile (320px) to desktop (1200px+) screens.
- Use a clean, modern font like 'Segoe UI' or similar system fonts.
- Add keyboard support for all calculator functions.
- Include subtle sound effects or haptic feedback simulation on button clicks.""",
        description="A sophisticated calculator with modern UI and advanced features",
        requirements=[
            "Number buttons (0-9)",
            "Operation buttons (+, -, *, /)",
            "Equals button (=)",
            "Clear button (C or AC)",
            "Display screen for numbers and results",
            "Proper error handling for division by zero",
            "Responsive design",
        ],
        evaluation_criteria=[
            "Functional arithmetic operations",
            "Clean and intuitive UI design",
            "Proper button layout and sizing",
            "Error handling",
            "Visual appeal and styling",
            "Responsiveness",
        ],
        expected_features=[
            "Click handlers for all buttons",
            "Display updates",
            "Calculation logic",
            "Error messages",
            "Modern CSS styling",
        ],
        time_estimate_minutes=15,
        tags=["calculator", "basic", "arithmetic", "ui"],
    ),
    "scientific_calculator": TaskDefinition(
        name="scientific_calculator",
        category=TaskCategory.CALCULATOR,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Create a comprehensive scientific calculator with advanced mathematical functions and professional design.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a professional scientific calculator interface with a sophisticated dark theme using deep grays and subtle blue accents.
- Include all basic arithmetic operations plus advanced functions: trigonometric (sin, cos, tan, asin, acos, atan), logarithmic (log, ln), exponential (exp, x^y), square root, factorial, and parentheses.
- Add memory functions (M+, M-, MR, MC, MS) with clear visual indicators when memory contains values.
- Implement degree/radian mode toggle with clear visual indication of current mode.
- The display should show both the current input and calculation history.
- Add scientific notation support for very large or small numbers.
- Include comprehensive error handling for domain errors, overflow, and invalid operations.
- Buttons should be organized logically with color coding for different function types.
- Add keyboard support for all functions with helpful tooltips showing keyboard shortcuts.
- The calculator must be fully responsive while maintaining the professional scientific calculator layout.""",
        description="A comprehensive scientific calculator with advanced mathematical functions",
        requirements=[
            "All basic calculator functions",
            "Trigonometric functions (sin, cos, tan)",
            "Inverse trigonometric functions",
            "Logarithmic functions (log, ln)",
            "Exponential and power functions",
            "Square root and nth root",
            "Parentheses support",
            "Memory functions",
            "Degree/Radian mode toggle",
        ],
        evaluation_criteria=[
            "Comprehensive function set",
            "Accurate calculations",
            "Professional appearance",
            "Proper function grouping",
            "Mode indicators",
            "Complex expression handling",
        ],
        expected_features=[
            "Extended button layout",
            "Mode switching",
            "Memory operations",
            "Expression parsing",
            "Scientific notation support",
        ],
        time_estimate_minutes=30,
        tags=["calculator", "scientific", "advanced", "mathematics"],
    ),
    # Website Tasks
    "personal_portfolio": TaskDefinition(
        name="personal_portfolio",
        category=TaskCategory.PORTFOLIO,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Create a stunning, professional portfolio website for a web developer with cutting-edge design and animations.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a modern, dark-themed portfolio with a sophisticated color scheme of deep navy, electric blue accents, and white text.
- Include a fixed navigation header with smooth scroll-to-section functionality.
- Hero section: Large name/title, professional photo placeholder, animated typing effect for roles, and compelling call-to-action.
- About section: Personal story, professional journey, and key achievements with timeline animation.
- Skills section: Interactive skill bars with percentage animations, technology icons, and hover effects.
- Projects section: Grid of project cards with image placeholders, descriptions, tech stack tags, and 'View Project' buttons with hover effects.
- Contact section: Professional contact form with validation, social media links with icon animations.
- Footer: Additional links and copyright information.
- Implement smooth scrolling, parallax effects, fade-in animations on scroll, and interactive elements throughout.
- The site must be fully responsive with mobile-first design approach.
- Add a dark/light theme toggle with smooth transition animations.""",
        description="A stunning professional portfolio with advanced animations and modern design",
        requirements=[
            "Responsive navigation header",
            "Hero section with call-to-action",
            "About section with personal info",
            "Skills section with visual indicators",
            "Projects showcase with cards/grid",
            "Contact form with validation",
            "Footer with social links",
            "Smooth scrolling navigation",
            "Mobile-responsive design",
        ],
        evaluation_criteria=[
            "Professional appearance",
            "Responsive design quality",
            "Navigation functionality",
            "Content organization",
            "Visual hierarchy",
            "Interactive elements",
            "Form functionality",
        ],
        expected_features=[
            "Multi-section layout",
            "CSS animations/transitions",
            "Form validation",
            "Responsive grid systems",
            "Modern typography",
            "Color scheme consistency",
        ],
        time_estimate_minutes=45,
        tags=["portfolio", "website", "responsive", "professional"],
    ),
    "restaurant_website": TaskDefinition(
        name="restaurant_website",
        category=TaskCategory.WEBSITE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Create a comprehensive restaurant website with elegant design.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a warm, inviting layout using a sophisticated color palette of rich burgundy, warm gold, cream, and earthy browns.
- Include a professional header with restaurant logo placeholder and navigation menu (Home, Menu, About, Gallery, Location, Reservations).
- Hero section: Large, appetizing food image background with restaurant name overlay and compelling tagline.
- About section: Restaurant story, chef information, and culinary philosophy with elegant typography.
- Menu section: Categorized food items (Appetizers, Mains, Desserts, Beverages) with descriptions, prices, and attractive layout.
- Gallery section: Grid of food photography placeholders with proper styling and layout.
- Location section: Address, hours of operation, contact information, and embedded map placeholder.
- Reservation section: Booking form with proper styling and form elements displayed.
- Footer: Social media links, additional contact info, and legal information.
- The design must be fully responsive with food-focused imagery and warm, inviting atmosphere throughout.
- Focus on excellent visual hierarchy, typography, and professional restaurant branding.""",
        description="A comprehensive restaurant website with elegant design and professional appearance",
        requirements=[
            "Attractive header with branding",
            "Hero section with food imagery",
            "Restaurant story/about section",
            "Categorized menu with prices",
            "Photo gallery",
            "Location and hours information",
            "Reservation booking form",
            "Contact information",
            "Food-themed design",
        ],
        evaluation_criteria=[
            "Visual appeal and food presentation",
            "Menu organization and readability",
            "Booking form functionality",
            "Brand consistency",
            "Information accessibility",
            "Mobile optimization",
        ],
        expected_features=[
            "Image galleries",
            "Menu categorization",
            "Reservation form",
            "Location integration",
            "Responsive images",
            "Themed styling",
        ],
        time_estimate_minutes=40,
        tags=["restaurant", "website", "menu", "booking", "business"],
    ),
    # Dashboard Tasks
    "analytics_dashboard": TaskDefinition(
        name="analytics_dashboard",
        category=TaskCategory.DASHBOARD,
        difficulty=DifficultyLevel.ADVANCED,
        prompt="Create a comprehensive analytics dashboard with multiple data visualization components. Include: header with user profile and notifications, sidebar navigation, main content area with KPI cards showing key metrics, various charts (line chart for trends, bar chart for comparisons, pie chart for distributions, donut chart for categories), data tables with sorting and filtering, and a responsive grid layout. Use a modern, professional design with a dark/light theme toggle.",
        description="A comprehensive analytics dashboard with multiple visualization components",
        requirements=[
            "Dashboard header with user info",
            "Sidebar navigation menu",
            "KPI cards with key metrics",
            "Multiple chart types (line, bar, pie, donut)",
            "Data tables with sorting/filtering",
            "Responsive grid layout",
            "Theme toggle (dark/light)",
            "Interactive chart elements",
            "Export functionality mockup",
        ],
        evaluation_criteria=[
            "Data visualization quality",
            "Layout organization",
            "Interactive elements",
            "Theme implementation",
            "Professional appearance",
            "Responsive behavior",
            "Chart variety and accuracy",
        ],
        expected_features=[
            "CSS Grid/Flexbox layouts",
            "Chart.js or similar implementation",
            "Theme switching logic",
            "Interactive data tables",
            "Responsive design patterns",
            "Modern UI components",
        ],
        time_estimate_minutes=60,
        tags=["dashboard", "analytics", "charts", "data", "advanced"],
    ),
    # Game Tasks
    "tic_tac_toe": TaskDefinition(
        name="tic_tac_toe",
        category=TaskCategory.GAME,
        difficulty=DifficultyLevel.BEGINNER,
        prompt="Create an interactive Tic-Tac-Toe game with a 3x3 grid. Include player turn indicators, win detection, draw detection, score tracking, and a reset button. Make it visually appealing with hover effects, winning line highlighting, and smooth animations. Add a simple AI opponent option.",
        description="An interactive Tic-Tac-Toe game with AI opponent",
        requirements=[
            "3x3 game grid",
            "Player turn indicators",
            "Win/draw detection",
            "Score tracking",
            "Reset game functionality",
            "Hover effects on cells",
            "Winning line highlighting",
            "Simple AI opponent",
            "Game state management",
        ],
        evaluation_criteria=[
            "Game logic correctness",
            "User interface quality",
            "Animation smoothness",
            "AI implementation",
            "Score tracking accuracy",
            "Visual feedback quality",
        ],
        expected_features=[
            "Click event handlers",
            "Game state logic",
            "Win condition checking",
            "AI move calculation",
            "CSS animations",
            "Score persistence",
        ],
        time_estimate_minutes=25,
        tags=["game", "interactive", "ai", "logic", "animation"],
    ),
    "memory_card_game": TaskDefinition(
        name="memory_card_game",
        category=TaskCategory.GAME,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="Create a memory card matching game with a grid of face-down cards. Players click to flip cards and try to find matching pairs. Include: difficulty levels (4x4, 6x6, 8x8 grids), timer, move counter, high score tracking, card flip animations, match animations, and a congratulations screen when completed. Use colorful, engaging card designs.",
        description="A memory card matching game with multiple difficulty levels",
        requirements=[
            "Multiple grid sizes (4x4, 6x6, 8x8)",
            "Card flip animations",
            "Match detection and animations",
            "Timer functionality",
            "Move counter",
            "High score system",
            "Difficulty selection",
            "Game completion celebration",
            "Colorful card designs",
        ],
        evaluation_criteria=[
            "Game mechanics accuracy",
            "Animation quality",
            "Difficulty progression",
            "Score system implementation",
            "Visual appeal",
            "User experience flow",
        ],
        expected_features=[
            "Dynamic grid generation",
            "Card shuffling algorithm",
            "Animation sequences",
            "Timer implementation",
            "Local storage for scores",
            "Responsive card layouts",
        ],
        time_estimate_minutes=35,
        tags=["game", "memory", "animation", "difficulty", "scoring"],
    ),
    # Form Tasks
    "contact_form": TaskDefinition(
        name="contact_form",
        category=TaskCategory.FORM,
        difficulty=DifficultyLevel.BEGINNER,
        prompt="Create a comprehensive contact form with proper validation and user feedback. Include fields for: name, email, phone number, subject, message, and a submit button. Add real-time validation with error messages, success confirmation, required field indicators, and proper form styling with focus states and hover effects.",
        description="A comprehensive contact form with validation and user feedback",
        requirements=[
            "Name, email, phone, subject, message fields",
            "Real-time field validation",
            "Required field indicators",
            "Error message display",
            "Success confirmation",
            "Form submission handling",
            "Proper input styling",
            "Focus and hover states",
            "Responsive design",
        ],
        evaluation_criteria=[
            "Validation accuracy",
            "User feedback quality",
            "Form styling and UX",
            "Error handling",
            "Accessibility features",
            "Mobile responsiveness",
        ],
        expected_features=[
            "Input validation logic",
            "Error message system",
            "Form state management",
            "CSS form styling",
            "Responsive form layout",
            "Success/error feedback",
        ],
        time_estimate_minutes=20,
        tags=["form", "validation", "ux", "responsive", "feedback"],
    ),
    "survey_form": TaskDefinition(
        name="survey_form",
        category=TaskCategory.FORM,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="Create a multi-step survey form with various input types. Include: text inputs, radio buttons, checkboxes, dropdown selects, range sliders, file upload, textarea, and date picker. Add progress indicator, step navigation (next/previous), form validation, data persistence between steps, and a summary page before submission.",
        description="A multi-step survey form with various input types and progress tracking",
        requirements=[
            "Multiple form steps/pages",
            "Various input types (text, radio, checkbox, select, range, file, textarea, date)",
            "Progress indicator",
            "Step navigation buttons",
            "Form validation per step",
            "Data persistence between steps",
            "Summary page before submission",
            "Responsive design",
            "Smooth transitions between steps",
        ],
        evaluation_criteria=[
            "Input variety and functionality",
            "Step navigation smoothness",
            "Data persistence accuracy",
            "Progress indication clarity",
            "Validation completeness",
            "Summary page accuracy",
        ],
        expected_features=[
            "Multi-step form logic",
            "Data storage between steps",
            "Progress calculation",
            "Step validation",
            "Transition animations",
            "Form data summary",
        ],
        time_estimate_minutes=40,
        tags=["form", "multi-step", "survey", "validation", "progress"],
    ),
    # Visualization Tasks
    "data_table": TaskDefinition(
        name="data_table",
        category=TaskCategory.VISUALIZATION,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="Create an advanced data table with interactive features. Display sample employee data with columns for: ID, Name, Department, Position, Salary, Hire Date, and Status. Include: sortable columns, search/filter functionality, pagination, row selection, export options (CSV/JSON), column visibility toggles, and responsive design that adapts to mobile screens.",
        description="An advanced data table with sorting, filtering, and export capabilities",
        requirements=[
            "Sample employee dataset",
            "Sortable column headers",
            "Global search functionality",
            "Column-specific filters",
            "Pagination with page size options",
            "Row selection (single/multiple)",
            "Export functionality (CSV/JSON)",
            "Column visibility toggles",
            "Responsive table design",
            "Loading states and empty states",
        ],
        evaluation_criteria=[
            "Sorting functionality accuracy",
            "Search and filter effectiveness",
            "Pagination implementation",
            "Export feature functionality",
            "Mobile responsiveness",
            "Performance with large datasets",
        ],
        expected_features=[
            "Table sorting algorithms",
            "Search/filter logic",
            "Pagination calculations",
            "Data export functions",
            "Responsive table patterns",
            "State management",
        ],
        time_estimate_minutes=35,
        tags=["table", "data", "sorting", "filtering", "export", "responsive"],
    ),
    # Interactive Tasks
    "image_gallery": TaskDefinition(
        name="image_gallery",
        category=TaskCategory.INTERACTIVE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="Create an interactive image gallery with lightbox functionality. Include: thumbnail grid layout, category filtering, search functionality, lightbox modal for full-size viewing, navigation arrows in lightbox, image zoom capability, slideshow mode, and responsive masonry layout. Use placeholder images with different categories like Nature, Architecture, People, etc.",
        description="An interactive image gallery with lightbox and filtering capabilities",
        requirements=[
            "Thumbnail grid with masonry layout",
            "Category filtering buttons",
            "Search functionality",
            "Lightbox modal for full-size viewing",
            "Navigation arrows in lightbox",
            "Image zoom in/out functionality",
            "Slideshow/autoplay mode",
            "Responsive design",
            "Loading animations",
            "Keyboard navigation support",
        ],
        evaluation_criteria=[
            "Gallery layout quality",
            "Lightbox functionality",
            "Filtering accuracy",
            "Navigation smoothness",
            "Zoom implementation",
            "Mobile touch support",
        ],
        expected_features=[
            "Masonry/grid layouts",
            "Modal implementation",
            "Image preloading",
            "Touch/swipe gestures",
            "Keyboard event handling",
            "Responsive image handling",
        ],
        time_estimate_minutes=45,
        tags=["gallery", "lightbox", "interactive", "responsive", "modal"],
    ),
    "todo_app": TaskDefinition(
        name="todo_app",
        category=TaskCategory.INTERACTIVE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Create a feature-rich, modern todo list application with beautiful UI design.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a clean, modern interface with a light theme using soft blues, whites, and subtle gray accents.
- Include a header with app title, add-new-task input field, and task statistics display.
- Show sample tasks in different states: active tasks, completed tasks (with strikethrough), and various priority levels.
- Display task filtering options: All, Active, Completed buttons with proper styling.
- Include a search bar with proper styling for task filtering.
- Show tasks with priority levels (High, Medium, Low) using color-coded indicators.
- Display due dates and show some tasks as overdue with visual indicators.
- Include task categories/tags with color coding for visual organization.
- Show edit and delete buttons for each task with proper icon styling.
- Design task items with checkboxes, task text, priority indicators, and action buttons.
- The app must be fully responsive with mobile-friendly layout and touch-friendly button sizes.""",
        description="A feature-rich todo application with modern UI and excellent visual design",
        requirements=[
            "Add/edit/delete tasks",
            "Mark tasks complete/incomplete",
            "Task filtering (all/active/completed)",
            "Search functionality",
            "Drag-and-drop reordering",
            "Due dates with date picker",
            "Priority levels (high/medium/low)",
            "Categories/tags system",
            "Local storage persistence",
            "Export/import tasks (JSON)",
            "Task statistics/summary",
        ],
        evaluation_criteria=[
            "Task management functionality",
            "Drag-and-drop implementation",
            "Data persistence accuracy",
            "Search and filter effectiveness",
            "User interface intuitiveness",
            "Feature completeness",
        ],
        expected_features=[
            "CRUD operations for tasks",
            "Drag-and-drop API usage",
            "Local storage management",
            "Date handling and validation",
            "Search algorithms",
            "Data export/import logic",
        ],
        time_estimate_minutes=50,
        tags=["todo", "crud", "drag-drop", "persistence", "productivity"],
    ),
    "modern_landing_page": TaskDefinition(
        name="modern_landing_page",
        category=TaskCategory.WEBSITE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Design a visually striking landing page for a fictional SaaS product called 'SynthWave'.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The design should be dark-themed, using a palette of deep purples, electric blues, and neon pinks.
- Use a bold, futuristic font for the main headline and a clean, readable sans-serif font for the body text.
- The layout should be a single, centered column.
- It must include a hero section with the product name 'SynthWave' and a prominent call-to-action button.
- Add three distinct sections below the hero: 'Features', 'Pricing', and a simple 'Contact' layout.
- The call-to-action button should have a subtle glowing animation on hover.
- Ensure the page is fully responsive and looks polished on mobile, tablet, and desktop screens.""",
        description="A dark-themed, futuristic landing page for a SaaS product",
        requirements=[
            "Dark theme with purple, blue, and pink color scheme",
            "Hero section with product name and CTA",
            "Features section with key product benefits",
            "Pricing section with plan options",
            "Contact section with form or information",
            "Futuristic typography and design elements",
            "Glowing button animations",
            "Fully responsive layout",
            "Single HTML file with inline CSS/JS",
        ],
        evaluation_criteria=[
            "Visual impact and design aesthetics",
            "Color scheme implementation",
            "Typography and readability",
            "Animation quality and smoothness",
            "Responsive design effectiveness",
            "User experience flow",
        ],
        expected_features=[
            "CSS animations and transitions",
            "Responsive grid layouts",
            "Modern CSS techniques",
            "Interactive button effects",
            "Mobile-optimized design",
        ],
        time_estimate_minutes=30,
        tags=["landing-page", "saas", "dark-theme", "futuristic", "responsive"],
    ),
    "minimalist_blog_layout": TaskDefinition(
        name="minimalist_blog_layout",
        category=TaskCategory.WEBSITE,
        difficulty=DifficultyLevel.BEGINNER,
        prompt="""Create the layout for a minimalist and elegant blog.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The design must be clean and content-focused, with a light color scheme (primarily white and light gray) and a single accent color for links.
- Use a classic, highly readable serif font for the blog post body and a modern sans-serif for headings.
- The layout should feature a simple header with the blog's title, a main content area with a placeholder title and text for a single blog post, and a minimal footer.
- The page must be fully responsive, with typography and spacing that adapt beautifully to different screen sizes.""",
        description="A clean, minimalist, and content-focused blog layout",
        requirements=[
            "Light, clean color scheme",
            "Simple header with blog title",
            "Main content area with blog post",
            "Typography-focused design",
            "Minimal footer",
            "Responsive layout",
            "Single HTML file structure",
            "Serif font for body text",
            "Sans-serif for headings",
        ],
        evaluation_criteria=[
            "Typography quality and readability",
            "Visual hierarchy and spacing",
            "Minimalist design execution",
            "Responsive behavior",
            "Content focus and clarity",
            "Overall aesthetic appeal",
        ],
        expected_features=[
            "Responsive typography",
            "Clean CSS architecture",
            "Optimal reading experience",
            "Mobile-friendly layout",
            "Professional appearance",
        ],
        time_estimate_minutes=20,
        tags=["blog", "minimalist", "typography", "content", "clean"],
    ),
    "ecommerce_product_page": TaskDefinition(
        name="ecommerce_product_page",
        category=TaskCategory.WEBSITE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Construct a product detail page for a high-end wristwatch.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The visual style should be luxurious and elegant, using a sophisticated color palette (e.g., charcoal, gold, and off-white).
- On a desktop, the layout should be a two-column grid: the left for a product image placeholder and the right for the watch's name, a short description, the price, and an 'Add to Cart' button.
- On mobile devices, these two columns should stack vertically.
- Use a classic serif font for headings and a clean sans-serif for body text.
- The 'Add to Cart' button should have a premium look with a subtle animation on click.
- The page must be fully responsive.""",
        description="An elegant and luxurious product page for a high-end watch",
        requirements=[
            "Luxurious color scheme (charcoal, gold, off-white)",
            "Two-column desktop layout",
            "Product image placeholder",
            "Product name and description",
            "Price display",
            "Add to Cart button with animation",
            "Mobile-responsive stacking layout",
            "Premium typography",
            "Elegant design aesthetic",
        ],
        evaluation_criteria=[
            "Luxury brand aesthetic execution",
            "Layout responsiveness",
            "Typography and color harmony",
            "Button design and animations",
            "Mobile experience quality",
            "Overall premium feel",
        ],
        expected_features=[
            "CSS Grid/Flexbox layouts",
            "Responsive design patterns",
            "Premium button styling",
            "Mobile-first approach",
            "Elegant animations",
        ],
        time_estimate_minutes=25,
        tags=["ecommerce", "luxury", "product", "responsive", "premium"],
    ),
    "travel_website_hero": TaskDefinition(
        name="travel_website_hero",
        category=TaskCategory.WEBSITE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Design a visually immersive hero section for a travel website.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The design should evoke a sense of adventure, using a vibrant color scheme inspired by nature (e.g., deep blues, lush greens).
- The layout should feature a large, bold, and inspiring headline font over a placeholder for a full-width background image.
- A clean and modern search bar for destinations should be centered over the background.
- The entire section must be fully responsive, ensuring the text is always readable and the layout is well-balanced on all devices.""",
        description="An immersive and visually beautiful hero section for a travel website",
        requirements=[
            "Nature-inspired color scheme",
            "Full-width background image placeholder",
            "Large, inspiring headline",
            "Centered destination search bar",
            "Adventure-themed design",
            "Fully responsive layout",
            "Text readability over background",
            "Modern search interface",
            "Balanced visual composition",
        ],
        evaluation_criteria=[
            "Visual impact and inspiration",
            "Color scheme effectiveness",
            "Typography over background",
            "Search bar design and placement",
            "Responsive layout quality",
            "Adventure theme execution",
        ],
        expected_features=[
            "CSS background techniques",
            "Overlay effects for text readability",
            "Responsive search interface",
            "Modern form styling",
            "Mobile-optimized layout",
        ],
        time_estimate_minutes=25,
        tags=["travel", "hero", "search", "adventure", "nature"],
    ),
    "photography_portfolio_gallery": TaskDefinition(
        name="photography_portfolio_gallery",
        category=TaskCategory.PORTFOLIO,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Create a gallery page for a photography portfolio.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The design should be image-centric and minimalist, with a dark background to make the (placeholder) images stand out.
- The gallery should be a responsive grid of placeholders for photos.
- On hover, each placeholder should have a subtle zoom effect.
- The page needs a simple header with the photographer's name and a footer with social media icon placeholders.
- The grid layout must be fluid, adapting from a single column on mobile to multiple columns on wider screens.""",
        description="A minimalist, image-focused gallery for a photography portfolio",
        requirements=[
            "Dark background for image emphasis",
            "Responsive grid layout",
            "Photo placeholder grid",
            "Hover zoom effects",
            "Simple header with photographer name",
            "Footer with social media icons",
            "Fluid column adaptation",
            "Minimalist design approach",
            "Image-centric layout",
        ],
        evaluation_criteria=[
            "Grid layout responsiveness",
            "Hover effect quality",
            "Image presentation effectiveness",
            "Minimalist design execution",
            "Mobile adaptation quality",
            "Professional portfolio appearance",
        ],
        expected_features=[
            "CSS Grid or Flexbox layouts",
            "CSS hover transitions",
            "Responsive breakpoints",
            "Image aspect ratio handling",
            "Professional typography",
        ],
        time_estimate_minutes=30,
        tags=["photography", "portfolio", "gallery", "grid", "minimalist"],
    ),
    "recipe_card_display": TaskDefinition(
        name="recipe_card_display",
        category=TaskCategory.WEBSITE,
        difficulty=DifficultyLevel.BEGINNER,
        prompt="""Design a single, visually appealing recipe card as a web page.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The style should be warm and inviting, using a color palette reminiscent of a kitchen (e.g., warm browns, creamy whites, a splash of herbal green).
- The layout should be well-organized with clear sections for the recipe title, a short description, an ingredients list, and step-by-step instructions.
- Use a charming, slightly rustic font for headings and a clear, legible font for the body.
- The page must be fully responsive, so the recipe is easy to read on a phone or a larger screen.""",
        description="A warm and inviting, well-organized recipe card",
        requirements=[
            "Warm, kitchen-inspired color palette",
            "Recipe title section",
            "Short description area",
            "Organized ingredients list",
            "Step-by-step instructions",
            "Rustic typography for headings",
            "Clear, legible body font",
            "Fully responsive layout",
            "Easy mobile reading experience",
        ],
        evaluation_criteria=[
            "Color palette warmth and appeal",
            "Content organization clarity",
            "Typography readability",
            "Mobile usability",
            "Kitchen theme execution",
            "Overall visual appeal",
        ],
        expected_features=[
            "Warm color CSS styling",
            "Organized content structure",
            "Responsive typography",
            "Mobile-friendly layout",
            "Clear visual hierarchy",
        ],
        time_estimate_minutes=20,
        tags=["recipe", "food", "card", "warm", "kitchen"],
    ),
    "event_announcement_page": TaskDefinition(
        name="event_announcement_page",
        category=TaskCategory.WEBSITE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Create a stylish announcement page for a virtual tech conference.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The design should be modern and tech-savvy, with a dark theme that uses gradients of blue and purple.
- The typography should be clean and futuristic.
- The page should have a prominent headline with the event name and date.
- Below the headline, include sections for a keynote speaker (with a placeholder for their photo and bio) and a large 'Register Now' button.
- The 'Register Now' button should be a focal point with an eye-catching hover effect.
- The layout must be fully responsive and look professional on all devices.""",
        description="A modern and stylish announcement page for a virtual tech conference",
        requirements=[
            "Modern, tech-savvy dark theme",
            "Blue and purple gradient colors",
            "Clean, futuristic typography",
            "Prominent event name and date",
            "Keynote speaker section",
            "Speaker photo placeholder and bio",
            "Large 'Register Now' button",
            "Eye-catching button hover effects",
            "Fully responsive layout",
            "Professional appearance",
        ],
        evaluation_criteria=[
            "Modern tech aesthetic execution",
            "Gradient implementation quality",
            "Typography and futuristic feel",
            "Button design and hover effects",
            "Content hierarchy and flow",
            "Professional presentation",
        ],
        expected_features=[
            "CSS gradients and modern styling",
            "Interactive button animations",
            "Responsive layout techniques",
            "Professional typography",
            "Tech conference branding",
        ],
        time_estimate_minutes=25,
        tags=["event", "tech", "conference", "announcement", "modern"],
    ),
    "weather_dashboard": TaskDefinition(
        name="weather_dashboard",
        category=TaskCategory.DASHBOARD,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Create a comprehensive weather dashboard with real-time-style interface and interactive elements.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a modern, clean interface with a gradient background transitioning from light blue to deep blue.
- Include a prominent header with "Weather Dashboard" title and current date/time display that updates via JavaScript.
- Main content area should feature:
  * Current weather section: Large temperature display (72°F), weather icon placeholder, humidity (65%), wind speed (12 mph), UV index (6)
  * 5-day forecast: Horizontal cards showing day, weather icon, high/low temps
  * Hourly forecast: Scrollable horizontal timeline with hourly data for next 12 hours
  * Weather map section: Placeholder for interactive map with zoom controls
  * Air quality index: Visual indicator with color-coded AQI scale (Good/Moderate/Unhealthy)
- Add location search bar with autocomplete styling and "Use Current Location" button
- Include weather alerts section with sample severe weather warnings
- Weather metrics should use realistic sample data and proper units
- Implement smooth transitions, hover effects, and interactive elements throughout
- The dashboard must be fully responsive with mobile-optimized layouts
- Use modern weather icons (Unicode symbols or CSS-created icons) and consistent color coding for different weather conditions""",
        description="A comprehensive weather dashboard with current conditions, forecasts, and interactive elements",
        requirements=[
            "Current weather display with temperature, humidity, wind",
            "5-day forecast with weather icons",
            "Hourly forecast timeline",
            "Location search with geolocation option",
            "Weather map placeholder with controls",
            "Air quality index display",
            "Weather alerts section",
            "Real-time clock and date",
            "Responsive design for all devices",
            "Interactive hover effects and transitions",
        ],
        evaluation_criteria=[
            "Data organization and presentation clarity",
            "Interactive elements functionality",
            "Visual design and weather iconography",
            "Responsive layout quality",
            "Information hierarchy effectiveness",
            "Mobile usability and touch interactions",
        ],
        expected_features=[
            "JavaScript for time updates and interactions",
            "CSS Grid and Flexbox for complex layouts",
            "Weather data visualization techniques",
            "Responsive breakpoints and mobile optimization",
            "Modern UI components and animations",
        ],
        time_estimate_minutes=50,
        tags=["weather", "dashboard", "interactive", "real-time", "responsive"],
    ),
    "fitness_tracker_app": TaskDefinition(
        name="fitness_tracker_app",
        category=TaskCategory.INTERACTIVE,
        difficulty=DifficultyLevel.ADVANCED,
        prompt="""Create a comprehensive fitness tracking application with workout logging and progress visualization.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a modern, health-focused interface using energetic colors: vibrant orange (#FF6B35), fresh green (#4ECDC4), and clean whites/grays.
- Include a dashboard header with user profile section, daily step counter (8,247 steps), calories burned (1,847 cal), and water intake tracker (6/8 glasses).
- Main sections should include:
  * Today's Activity: Visual progress rings for steps, calories, and active minutes with percentage completion
  * Workout Logger: Form to add new workouts with exercise type dropdown (Cardio, Strength, Yoga, Sports), duration, intensity level, and notes
  * Recent Workouts: List of recent activities with edit/delete options, showing date, exercise, duration, and calories
  * Weekly Progress: Chart visualization showing daily activity over the past 7 days
  * Goal Setting: Interface to set and track fitness goals with progress bars
  * Achievement Badges: Grid of earned fitness milestones with colorful badge designs
- Implement local storage to persist workout data and user preferences
- Add workout timer functionality with start/pause/stop controls and time display
- Include exercise suggestions and quick-add buttons for common activities
- The app must be fully responsive with mobile-first design and touch-friendly controls
- Add smooth animations for progress indicators, form interactions, and page transitions""",
        description="A comprehensive fitness tracking app with workout logging, progress visualization, and goal tracking",
        requirements=[
            "User dashboard with daily metrics",
            "Workout logging form with multiple input types",
            "Progress visualization with charts/rings",
            "Recent activity history with CRUD operations",
            "Goal setting and tracking interface",
            "Achievement badge system",
            "Workout timer with controls",
            "Local storage for data persistence",
            "Exercise suggestions and quick-add features",
            "Mobile-responsive design with touch optimization",
        ],
        evaluation_criteria=[
            "Fitness tracking functionality completeness",
            "Data visualization effectiveness",
            "User interface intuitiveness for fitness users",
            "Mobile usability and touch interactions",
            "Progress tracking accuracy and visual appeal",
            "Local storage implementation and data persistence",
        ],
        expected_features=[
            "Complex form handling and validation",
            "JavaScript for timers and calculations",
            "Local storage management for workout data",
            "CSS animations for progress indicators",
            "Responsive design with mobile optimization",
            "CRUD operations for workout management",
        ],
        time_estimate_minutes=65,
        tags=["fitness", "tracking", "health", "mobile", "progressive", "advanced"],
    ),
    "music_streaming_interface": TaskDefinition(
        name="music_streaming_interface",
        category=TaskCategory.INTERACTIVE,
        difficulty=DifficultyLevel.ADVANCED,
        prompt="""Create a modern music streaming application interface with playlist management and audio controls.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a sleek, dark-themed interface inspired by modern music apps using deep blacks (#121212), rich purples (#7B68EE), and accent greens (#1DB954).
- Layout should include:
  * Left Sidebar: Navigation menu (Home, Browse, Library, Playlists), user playlists list, and recently played section
  * Main Content Area: Featured playlists grid, new releases carousel, recommended songs list with album art placeholders
  * Right Sidebar: Now playing section with large album art, song info, and queue display
  * Bottom Player Bar: Audio controls (previous, play/pause, next, shuffle, repeat), progress bar, volume control, and current song info
- Implement interactive features:
  * Playlist creation and management with drag-and-drop song reordering
  * Search functionality with real-time filtering of songs and artists
  * Heart/like buttons for songs with animation feedback
  * Volume slider with visual feedback
  * Progress bar that can be clicked to seek (simulated)
  * Play/pause button state changes with smooth animations
- Show sample music data with realistic artist names, song titles, album art placeholders, and durations
- Add hover effects for all interactive elements with smooth transitions
- Include context menus for songs (Add to Playlist, Remove, Share options)
- The interface must be fully responsive, adapting to tablet and mobile layouts
- Implement keyboard shortcuts for common actions (spacebar for play/pause, arrow keys for seek)""",
        description="A modern music streaming interface with playlist management, audio controls, and rich interactions",
        requirements=[
            "Three-panel layout (sidebar, main, now playing)",
            "Interactive audio player controls with progress bar",
            "Playlist creation and management system",
            "Search functionality with real-time filtering",
            "Drag-and-drop song reordering",
            "Volume control with visual feedback",
            "Song library with like/heart functionality",
            "Context menus for song actions",
            "Keyboard shortcut support",
            "Responsive design for multiple screen sizes",
        ],
        evaluation_criteria=[
            "Music app interface design authenticity",
            "Interactive controls functionality and responsiveness",
            "Playlist management system effectiveness",
            "Search and filtering implementation quality",
            "Drag-and-drop functionality smoothness",
            "Mobile adaptation and usability",
        ],
        expected_features=[
            "Complex multi-panel responsive layouts",
            "Drag-and-drop API implementation",
            "Real-time search filtering algorithms",
            "Advanced CSS animations and transitions",
            "Keyboard event handling and shortcuts",
            "Context menu implementation",
        ],
        time_estimate_minutes=70,
        tags=["music", "streaming", "audio", "playlist", "interactive", "advanced"],
    ),
    "expense_tracker_app": TaskDefinition(
        name="expense_tracker_app",
        category=TaskCategory.INTERACTIVE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Create a personal expense tracking application with budget management and spending analysis.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a clean, financial-focused interface using professional colors: navy blue (#1E3A8A), success green (#10B981), warning orange (#F59E0B), and neutral grays.
- Include a comprehensive header with current balance ($2,847.50), monthly budget progress bar, and quick add expense button.
- Main dashboard sections:
  * Monthly Overview: Large spending summary with budget vs. actual comparison and percentage completion
  * Expense Categories: Visual breakdown showing top spending categories (Food & Dining: $420, Transportation: $280, Entertainment: $180, Shopping: $320) with color-coded charts
  * Recent Transactions: Detailed list of latest expenses with date, description, category, and amount, plus edit/delete options
  * Add Expense Form: Modal or inline form with amount input, category dropdown, description field, date picker, and receipt upload placeholder
  * Budget Setting: Interface to set monthly budgets for different categories with visual progress indicators
  * Spending Analytics: Charts showing spending trends over time with month-over-month comparisons
- Implement expense categorization with predefined categories (Food, Transportation, Entertainment, Shopping, Bills, Healthcare, etc.)
- Add expense filtering by date range, category, and amount
- Include budget alerts and warnings when approaching limits
- Show spending insights and recommendations based on patterns
- Implement local storage to persist all financial data and user preferences
- Add export functionality to download expense reports
- The application must be fully responsive with mobile-optimized input methods
- Include data validation for all financial inputs and proper currency formatting""",
        description="A comprehensive expense tracking app with budget management, categorization, and spending analysis",
        requirements=[
            "Dashboard with balance and budget overview",
            "Expense categorization and management",
            "Transaction history with full CRUD operations",
            "Budget setting and progress tracking",
            "Spending analytics with charts and trends",
            "Expense filtering by multiple criteria",
            "Budget alerts and limit warnings",
            "Local storage for financial data persistence",
            "Export functionality for expense reports",
            "Mobile-responsive design with optimized inputs",
        ],
        evaluation_criteria=[
            "Financial data management accuracy",
            "Budget tracking functionality effectiveness",
            "User interface clarity for financial tasks",
            "Data visualization quality for spending insights",
            "Mobile usability for expense entry",
            "Data persistence and export features",
        ],
        expected_features=[
            "Complex financial calculations and validations",
            "Chart rendering for analytics visualization",
            "Advanced filtering and search capabilities",
            "Local storage management for financial data",
            "Modal interfaces for data entry",
            "Currency formatting and validation",
        ],
        time_estimate_minutes=55,
        tags=["finance", "budget", "tracking", "analytics", "mobile", "data"],
    ),
    "social_media_feed": TaskDefinition(
        name="social_media_feed",
        category=TaskCategory.INTERACTIVE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Create a modern social media feed interface with post interactions and real-time updates.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a contemporary social media layout using modern colors: clean whites, soft grays (#F8F9FA), accent blue (#1877F2), and interaction red (#E53E3E).
- Layout structure should include:
  * Top Navigation: Logo/brand name, search bar, notification bell icon (with badge), messages icon, and user profile dropdown
  * Left Sidebar: Quick navigation links (Home, Friends, Groups, Marketplace, Memories) and trending topics
  * Main Feed: Central area with post composition box and scrollable feed of posts
  * Right Sidebar: Friend suggestions, upcoming events, and sponsored content placeholders
- Post features to implement:
  * Create Post: Text area with character counter, photo upload button, emoji selector, and privacy settings dropdown
  * Post Display: User avatar, name, timestamp, post content, image placeholder, like/react buttons, comment count, share count
  * Interactive Elements: Like button with heart animation, comment sections that expand/collapse, share dropdown with options
  * Post Types: Text posts, photo posts with captions, shared content, and status updates
- Add sample posts with realistic social content, user interactions, and engagement metrics
- Implement infinite scroll behavior with loading animations
- Include story feature at top of feed with circular user avatars and "Add Story" option
- Add real-time-style notifications that appear and fade out
- Show online status indicators for friends and recent activity
- The interface must be fully responsive with mobile-first design and touch gestures
- Include dark mode toggle with smooth theme transitions""",
        description="A modern social media feed with post interactions, stories, and real-time updates",
        requirements=[
            "Complete social media layout with navigation and sidebars",
            "Post creation interface with media and privacy options",
            "Interactive post display with like, comment, share features",
            "Story feature with user avatars and add story option",
            "Infinite scroll with loading states",
            "Real-time notification system simulation",
            "Friend suggestions and social discovery",
            "Dark/light mode toggle with transitions",
            "Mobile-responsive design with touch optimization",
            "Character counters and input validation",
        ],
        evaluation_criteria=[
            "Social media interface authenticity and familiarity",
            "Post interaction functionality and responsiveness",
            "Feed layout and content organization",
            "Mobile usability and touch interactions",
            "Theme switching implementation quality",
            "Real-time features and notification system",
        ],
        expected_features=[
            "Complex multi-column responsive layouts",
            "Advanced JavaScript for interactions and animations",
            "Theme switching with CSS custom properties",
            "Infinite scroll implementation",
            "Modal interfaces for expanded content",
            "Character counting and input validation",
        ],
        time_estimate_minutes=60,
        tags=["social", "feed", "interactive", "real-time", "mobile", "modern"],
    ),
    "code_editor_interface": TaskDefinition(
        name="code_editor_interface",
        category=TaskCategory.INTERACTIVE,
        difficulty=DifficultyLevel.EXPERT,
        prompt="""Create a professional code editor interface with syntax highlighting and developer tools.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a developer-focused dark theme interface using professional colors: dark background (#1E1E1E), syntax highlighting colors (blue for keywords, green for strings, orange for numbers), and subtle UI accents.
- Layout should include:
  * Top Menu Bar: File menu (New, Open, Save, Export), Edit menu, View options, and Settings
  * Left Panel: File explorer tree with folders and files, search panel, and Git status indicator
  * Main Editor Area: Tabbed interface for multiple files with syntax-highlighted code display
  * Right Panel: Minimap of code, outline/symbol navigator, and extension marketplace
  * Bottom Panel: Terminal/console output, problems panel, and status bar with cursor position
- Code editor features to implement:
  * Line numbers with proper alignment and highlighting for current line
  * Syntax highlighting for multiple languages (HTML, CSS, JavaScript, Python) using realistic color schemes
  * Code folding indicators for functions and blocks
  * Find and replace functionality with regex support
  * Auto-completion suggestions popup
  * Multiple cursor support simulation
  * Bracket matching and highlighting
  * Indentation guides and whitespace visualization
- Add sample code files with proper syntax highlighting and realistic developer workflow
- Implement theme switching between dark, light, and high contrast modes
- Include keyboard shortcuts overlay and help system
- Add split-screen view for comparing files side by side
- Show Git integration with file status indicators (modified, new, deleted)
- The interface must be fully responsive while maintaining code editor usability
- Include settings panel for customizing editor behavior and appearance""",
        description="A professional code editor with syntax highlighting, file management, and developer tools",
        requirements=[
            "Multi-panel layout with file explorer and editor tabs",
            "Syntax highlighting for multiple programming languages",
            "Line numbers, code folding, and indentation guides",
            "Find/replace functionality with regex support",
            "Multiple theme support (dark, light, high contrast)",
            "Terminal/console integration panel",
            "Git status integration and file indicators",
            "Keyboard shortcuts and help system",
            "Split-screen editing capabilities",
            "Settings panel for editor customization",
        ],
        evaluation_criteria=[
            "Code editor interface authenticity and professionalism",
            "Syntax highlighting accuracy and visual appeal",
            "Developer workflow features completeness",
            "Multi-panel layout organization and usability",
            "Theme implementation and switching quality",
            "Keyboard navigation and shortcut integration",
        ],
        expected_features=[
            "Advanced CSS for syntax highlighting simulation",
            "Complex multi-panel responsive layouts",
            "JavaScript for editor interactions and shortcuts",
            "Theme switching with CSS custom properties",
            "Modal interfaces for settings and dialogs",
            "File tree navigation and tab management",
        ],
        time_estimate_minutes=80,
        tags=["code", "editor", "developer", "syntax", "professional", "expert"],
    ),
    "virtual_classroom": TaskDefinition(
        name="virtual_classroom",
        category=TaskCategory.INTERACTIVE,
        difficulty=DifficultyLevel.ADVANCED,
        prompt="""Create a comprehensive virtual classroom interface for online learning with video conferencing layout.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design an educational-focused interface using professional colors: education blue (#0066CC), success green (#28A745), neutral grays, and warm accents.
- Main layout should include:
  * Top Header: Class title "Advanced Web Development - Session 12", current time, participant count (24), and class controls
  * Video Grid: Main instructor video (large) with smaller participant video tiles in a responsive grid
  * Side Panel: Participant list with names, mic/camera status indicators, and hand raise icons
  * Bottom Panel: Chat interface with message history, emoji reactions, and file sharing buttons
  * Control Bar: Mic on/off, camera on/off, screen share, reactions, hand raise, and leave class buttons
- Interactive features to implement:
  * Participant management with mute controls and spotlight options
  * Chat system with real-time message display, private messaging options, and emoji reactions
  * Screen sharing simulation with presentation mode toggle
  * Whiteboard tool with drawing capabilities and collaboration features
  * Breakout rooms interface with room assignment and management
  * Recording controls and indicators
  * Attendance tracking with join/leave timestamps
  * Poll and quiz creation interface for real-time classroom engagement
- Add realistic classroom scenarios with sample participants, chat messages, and ongoing lesson content
- Include accessibility features like closed captions toggle and high contrast mode
- Implement bandwidth indicator and connection quality monitoring
- Show lesson materials panel with downloadable resources and assignment submissions
- The interface must be responsive for tablets and mobile devices with simplified controls
- Add teacher vs. student role permissions with different available features""",
        description="A comprehensive virtual classroom with video conferencing, chat, whiteboard, and teaching tools",
        requirements=[
            "Video conferencing layout with instructor and participant views",
            "Interactive chat system with emoji reactions and private messaging",
            "Participant management with mute controls and permissions",
            "Whiteboard and screen sharing simulation",
            "Breakout room management interface",
            "Real-time polls and quiz creation tools",
            "Lesson materials and resource sharing panel",
            "Recording controls and attendance tracking",
            "Accessibility features and connection monitoring",
            "Role-based permissions for teachers vs. students",
        ],
        evaluation_criteria=[
            "Virtual classroom interface completeness and realism",
            "Educational tool integration and usability",
            "Video conferencing layout organization",
            "Interactive features functionality and responsiveness",
            "Teacher workflow support and control options",
            "Student engagement features and accessibility",
        ],
        expected_features=[
            "Complex grid layouts for video conferencing simulation",
            "Real-time chat interface with message management",
            "Role-based UI customization",
            "Interactive whiteboard drawing simulation",
            "Modal interfaces for polls and breakout rooms",
            "Accessibility compliance and keyboard navigation",
        ],
        time_estimate_minutes=75,
        tags=["education", "video", "classroom", "interactive", "collaboration", "advanced"],
    ),
    "cryptocurrency_portfolio": TaskDefinition(
        name="cryptocurrency_portfolio",
        category=TaskCategory.DASHBOARD,
        difficulty=DifficultyLevel.ADVANCED,
        prompt="""Create a professional cryptocurrency portfolio dashboard with real-time market data visualization.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a sophisticated financial interface using crypto-themed colors: dark background (#0D1421), electric blue (#00D4FF), profit green (#00FF88), loss red (#FF4757), and gold accents (#FFD700).
- Dashboard layout should include:
  * Top Header: Total portfolio value ($47,893.24), 24h change (+$2,847.56 +6.32%), and market status indicator
  * Portfolio Overview: Pie chart showing asset allocation with percentages and current values
  * Holdings Table: Detailed list of owned cryptocurrencies with coin icons, amounts, current prices, 24h changes, and total values
  * Market Watchlist: Top cryptocurrencies with prices, charts, and quick trade buttons
  * Transaction History: Recent buy/sell orders with timestamps, amounts, and profit/loss calculations
  * News Feed: Cryptocurrency news headlines with source attribution and timestamp
- Advanced features to implement:
  * Price charts with candlestick patterns, moving averages, and technical indicators
  * Portfolio performance metrics including ROI, best/worst performers, and total gains/losses
  * Price alerts system with notification preferences and threshold settings
  * Currency conversion tools supporting multiple fiat currencies
  * DeFi integration panel showing staking rewards and yield farming opportunities
  * Tax reporting interface with transaction categorization and downloadable reports
  * Advanced analytics with risk assessment and diversification recommendations
- Add realistic cryptocurrency data with proper price formatting and market indicators
- Implement dark/light theme toggle optimized for financial data readability
- Include market sentiment indicators and fear/greed index display
- Show mining or staking rewards with APY calculations and compound interest projections
- The dashboard must be responsive with mobile-optimized trading controls
- Add security features like two-factor authentication simulation and wallet connection status""",
        description="A professional crypto portfolio dashboard with market data, analytics, and trading features",
        requirements=[
            "Portfolio overview with total value and performance metrics",
            "Detailed holdings table with real-time price data simulation",
            "Interactive price charts with technical indicators",
            "Market watchlist with top cryptocurrencies",
            "Transaction history with profit/loss calculations",
            "Price alerts and notification system",
            "DeFi integration with staking and yield information",
            "Tax reporting and transaction categorization",
            "Market sentiment and analytics dashboard",
            "Mobile-responsive design with touch-optimized controls",
        ],
        evaluation_criteria=[
            "Financial dashboard professionalism and accuracy",
            "Cryptocurrency market data presentation quality",
            "Portfolio analytics depth and usefulness",
            "Chart visualization effectiveness and interactivity",
            "Mobile trading interface usability",
            "Security features implementation and prominence",
        ],
        expected_features=[
            "Advanced financial calculations and formatting",
            "Complex chart rendering for price data",
            "Real-time data simulation with JavaScript",
            "Responsive design optimized for financial workflows",
            "Advanced filtering and sorting for large datasets",
            "Security-focused UI patterns and indicators",
        ],
        time_estimate_minutes=70,
        tags=["crypto", "finance", "portfolio", "charts", "trading", "advanced"],
    ),
    "recipe_management_system": TaskDefinition(
        name="recipe_management_system",
        category=TaskCategory.INTERACTIVE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        prompt="""Create a comprehensive recipe management system with meal planning and shopping list generation.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a warm, kitchen-inspired interface using appetizing colors: warm orange (#FF8C42), fresh green (#8FBC8F), creamy white (#FFF8DC), and rich brown (#8B4513).
- Main application sections:
  * Recipe Library: Grid view of recipe cards with images, titles, ratings, prep time, and difficulty level
  * Recipe Details: Full recipe view with ingredients list, step-by-step instructions, nutritional information, and cooking tips
  * Meal Planner: Weekly calendar interface for planning breakfast, lunch, and dinner with drag-and-drop functionality
  * Shopping List: Auto-generated list from planned meals with checkoff capability and quantity adjustments
  * Recipe Creator: Form for adding new recipes with ingredient measurements, cooking instructions, and photo upload
  * My Favorites: Saved recipes with personal notes and modifications
- Advanced features to implement:
  * Recipe search and filtering by cuisine type, dietary restrictions, cooking time, and difficulty
  * Ingredient substitution suggestions with automatic measurement conversions
  * Nutritional calculator showing calories, macros, and dietary information per serving
  * Cooking timer integration with multiple simultaneous timers for different recipe steps
  * Recipe scaling functionality to adjust serving sizes with automatic measurement conversions
  * Recipe sharing and rating system with user reviews and comments
  * Meal prep planning with batch cooking optimization and storage recommendations
- Include realistic recipe database with various cuisines and dietary options (vegetarian, vegan, gluten-free, keto)
- Add grocery store organization for shopping lists with aisle categorization
- Implement recipe cost calculator with ingredient price tracking
- Show cooking technique tutorials and video placeholder integration
- The system must be fully responsive with mobile-optimized cooking mode
- Include voice control simulation for hands-free recipe reading while cooking""",
        description="A comprehensive recipe management system with meal planning, shopping lists, and cooking features",
        requirements=[
            "Recipe library with search, filtering, and categorization",
            "Detailed recipe display with ingredients and instructions",
            "Weekly meal planner with drag-and-drop functionality",
            "Automatic shopping list generation from meal plans",
            "Recipe creation and editing interface",
            "Nutritional information and dietary filtering",
            "Cooking timers and recipe scaling functionality",
            "Ingredient substitution and measurement conversion",
            "Meal prep planning and batch cooking optimization",
            "Mobile-responsive design with cooking mode optimization",
        ],
        evaluation_criteria=[
            "Recipe management functionality completeness",
            "Meal planning interface usability and efficiency",
            "Shopping list generation accuracy and organization",
            "Cooking workflow support and mobile optimization",
            "Search and filtering effectiveness",
            "Nutritional information presentation and accuracy",
        ],
        expected_features=[
            "Complex data management for recipes and ingredients",
            "Drag-and-drop meal planning interface",
            "Automatic calculation and conversion algorithms",
            "Advanced search and filtering implementations",
            "Timer functionality with multiple concurrent timers",
            "Mobile-optimized cooking interface with large touch targets",
        ],
        time_estimate_minutes=65,
        tags=["recipe", "cooking", "meal-planning", "food", "mobile", "kitchen"],
    ),
    "project_management_board": TaskDefinition(
        name="project_management_board",
        category=TaskCategory.INTERACTIVE,
        difficulty=DifficultyLevel.ADVANCED,
        prompt="""Create a comprehensive project management board with Kanban workflow and team collaboration features.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a professional productivity interface using modern colors: clean white (#FFFFFF), productivity blue (#0079BF), success green (#61BD4F), warning yellow (#F2D600), and urgent red (#EB5A46).
- Main board layout should include:
  * Project Header: Project name, description, team member avatars, and project progress indicators
  * Kanban Columns: Customizable workflow columns (Backlog, To Do, In Progress, Review, Done) with task counts
  * Task Cards: Detailed cards with title, description, assignee avatar, due date, priority indicator, and tag labels
  * Team Panel: Member list with roles, workload indicators, and availability status
  * Project Analytics: Burn-down charts, velocity tracking, and completion metrics
  * Activity Timeline: Recent project updates, comments, and team member actions
- Task management features to implement:
  * Drag-and-drop card movement between columns with smooth animations
  * Task creation modal with full details (title, description, assignee, due date, priority, checklist)
  * Task editing with inline comments, file attachments, and time tracking
  * Subtask management with progress tracking and dependency visualization
  * Label and tag system with color coding and filtering capabilities
  * Due date management with calendar integration and overdue alerts
  * Team member assignment with workload balancing and availability checking
- Advanced project features:
  * Sprint planning with story points and capacity management
  * Milestone tracking with deliverable management and deadline monitoring
  * Time tracking with manual entry and automatic timer functionality
  * Project templates for common workflows and quick project setup
  * Advanced filtering and search across all project data
  * Export capabilities for reports and stakeholder communication
- Add realistic project scenarios with sample tasks, team members, and project timelines
- Include notification system for task assignments, due dates, and project updates
- Show project templates and quick-start options for different project types
- The board must be fully responsive with mobile-optimized task management
- Implement dark/light theme with team preference synchronization""",
        description="A comprehensive project management board with Kanban workflow, team collaboration, and analytics",
        requirements=[
            "Kanban board with customizable columns and drag-and-drop functionality",
            "Detailed task cards with assignees, dates, priorities, and labels",
            "Task creation and editing with full project management features",
            "Team management with member roles and workload tracking",
            "Project analytics with burn-down charts and velocity metrics",
            "Sprint planning and milestone tracking capabilities",
            "Time tracking with manual and automatic timer options",
            "Advanced filtering, search, and export functionality",
            "Notification system for project updates and deadlines",
            "Mobile-responsive design with touch-optimized task management",
        ],
        evaluation_criteria=[
            "Project management workflow completeness and efficiency",
            "Kanban board functionality and drag-and-drop smoothness",
            "Team collaboration features effectiveness",
            "Analytics and reporting quality and usefulness",
            "Mobile project management usability",
            "Professional appearance and productivity focus",
        ],
        expected_features=[
            "Advanced drag-and-drop with Kanban board logic",
            "Complex project data management and calculations",
            "Chart rendering for project analytics",
            "Modal interfaces for task management",
            "Real-time collaboration simulation",
            "Mobile-optimized touch interactions for productivity workflows",
        ],
        time_estimate_minutes=75,
        tags=["project", "management", "kanban", "team", "productivity", "advanced"],
    ),
}


def get_tasks_by_category(category: TaskCategory) -> List[TaskDefinition]:
    """Get all tasks in a specific category."""
    return [task for task in PREDEFINED_TASKS.values() if task.category == category]


def get_tasks_by_difficulty(difficulty: DifficultyLevel) -> List[TaskDefinition]:
    """Get all tasks of a specific difficulty level."""
    return [task for task in PREDEFINED_TASKS.values() if task.difficulty == difficulty]


def get_task_by_name(name: str) -> Optional[TaskDefinition]:
    """Get a specific task by name."""
    return PREDEFINED_TASKS.get(name)


def get_all_task_names() -> List[str]:
    """Get all available task names."""
    return list(PREDEFINED_TASKS.keys())
