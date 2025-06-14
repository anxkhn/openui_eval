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
