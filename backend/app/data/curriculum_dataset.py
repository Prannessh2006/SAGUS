from typing import List, Dict, Any


CONCEPTS: List[Dict[str, Any]] = [
    
    # Grade 1 - Basic Arithmetic
    {
        "id": "math_g1_counting",
        "name": "Counting Numbers",
        "description": "Understanding and counting whole numbers from 1 to 100. Students learn one-to-one correspondence and the concept of quantity.",
        "domain": "Mathematics",
        "grade_level": 1,
        "difficulty": 0.1,
        "keywords": ["numbers", "counting", "quantity", "whole numbers"],
        "curriculum_code": "MATH.1.NBT.1",
        "estimated_time_minutes": 30
    },
    {
        "id": "math_g1_addition_basic",
        "name": "Basic Addition",
        "description": "Adding two single-digit numbers with sums up to 20. Introduces the concept of combining quantities.",
        "domain": "Mathematics",
        "grade_level": 1,
        "difficulty": 0.15,
        "keywords": ["addition", "sum", "plus", "combining"],
        "curriculum_code": "MATH.1.OA.1",
        "estimated_time_minutes": 45
    },
    {
        "id": "math_g1_subtraction_basic",
        "name": "Basic Subtraction",
        "description": "Subtracting single-digit numbers from numbers up to 20. Introduces the concept of taking away.",
        "domain": "Mathematics",
        "grade_level": 1,
        "difficulty": 0.2,
        "keywords": ["subtraction", "minus", "difference", "taking away"],
        "curriculum_code": "MATH.1.OA.2",
        "estimated_time_minutes": 45
    },
    
    # Grade 2 - Extended Arithmetic
    {
        "id": "math_g2_place_value",
        "name": "Place Value",
        "description": "Understanding ones, tens, and hundreds places. Foundation for understanding larger numbers and operations.",
        "domain": "Mathematics",
        "grade_level": 2,
        "difficulty": 0.25,
        "keywords": ["place value", "ones", "tens", "hundreds", "digits"],
        "curriculum_code": "MATH.2.NBT.1",
        "estimated_time_minutes": 60
    },
    {
        "id": "math_g2_addition_two_digit",
        "name": "Two-Digit Addition",
        "description": "Adding two-digit numbers with and without regrouping. Builds on place value understanding.",
        "domain": "Mathematics",
        "grade_level": 2,
        "difficulty": 0.3,
        "keywords": ["addition", "two-digit", "regrouping", "carrying"],
        "curriculum_code": "MATH.2.NBT.5",
        "estimated_time_minutes": 60
    },
    {
        "id": "math_g2_subtraction_two_digit",
        "name": "Two-Digit Subtraction",
        "description": "Subtracting two-digit numbers with and without borrowing. Requires understanding of place value.",
        "domain": "Mathematics",
        "grade_level": 2,
        "difficulty": 0.35,
        "keywords": ["subtraction", "two-digit", "borrowing", "regrouping"],
        "curriculum_code": "MATH.2.NBT.6",
        "estimated_time_minutes": 60
    },
    
    # Grade 3 - Multiplication Introduction
    {
        "id": "math_g3_multiplication_intro",
        "name": "Introduction to Multiplication",
        "description": "Understanding multiplication as repeated addition. Learning multiplication facts for numbers 0-10.",
        "domain": "Mathematics",
        "grade_level": 3,
        "difficulty": 0.4,
        "keywords": ["multiplication", "times", "product", "repeated addition", "arrays"],
        "curriculum_code": "MATH.3.OA.1",
        "estimated_time_minutes": 90
    },
    {
        "id": "math_g3_division_intro",
        "name": "Introduction to Division",
        "description": "Understanding division as sharing and as the inverse of multiplication. Basic division facts.",
        "domain": "Mathematics",
        "grade_level": 3,
        "difficulty": 0.45,
        "keywords": ["division", "divide", "quotient", "sharing", "inverse"],
        "curriculum_code": "MATH.3.OA.2",
        "estimated_time_minutes": 90
    },
    {
        "id": "math_g3_fractions_intro",
        "name": "Introduction to Fractions",
        "description": "Understanding fractions as parts of a whole. Identifying numerators and denominators.",
        "domain": "Mathematics",
        "grade_level": 3,
        "difficulty": 0.5,
        "keywords": ["fractions", "numerator", "denominator", "parts of whole"],
        "curriculum_code": "MATH.3.NF.1",
        "estimated_time_minutes": 75
    },
    
    # Grade 4 - Advanced Multiplication & Fractions
    {
        "id": "math_g4_multi_digit_multiplication",
        "name": "Multi-Digit Multiplication",
        "description": "Multiplying multi-digit numbers using standard algorithms. Includes the distributive property.",
        "domain": "Mathematics",
        "grade_level": 4,
        "difficulty": 0.5,
        "keywords": ["multiplication", "multi-digit", "distributive property", "algorithm"],
        "curriculum_code": "MATH.4.NBT.5",
        "estimated_time_minutes": 90
    },
    {
        "id": "math_g4_long_division",
        "name": "Long Division",
        "description": "Dividing multi-digit numbers using the long division algorithm. Includes remainders.",
        "domain": "Mathematics",
        "grade_level": 4,
        "difficulty": 0.55,
        "keywords": ["division", "long division", "remainder", "algorithm"],
        "curriculum_code": "MATH.4.NBT.6",
        "estimated_time_minutes": 120
    },
    {
        "id": "math_g4_equivalent_fractions",
        "name": "Equivalent Fractions",
        "description": "Understanding and generating equivalent fractions. Comparing fractions with different denominators.",
        "domain": "Mathematics",
        "grade_level": 4,
        "difficulty": 0.5,
        "keywords": ["fractions", "equivalent", "compare", "denominator"],
        "curriculum_code": "MATH.4.NF.1",
        "estimated_time_minutes": 75
    },
    
    # Grade 5 - Decimals & Operations
    {
        "id": "math_g5_decimals_intro",
        "name": "Introduction to Decimals",
        "description": "Understanding decimal notation for fractions. Reading, writing, and comparing decimals.",
        "domain": "Mathematics",
        "grade_level": 5,
        "difficulty": 0.55,
        "keywords": ["decimals", "decimal point", "tenths", "hundredths"],
        "curriculum_code": "MATH.5.NBT.1",
        "estimated_time_minutes": 60
    },
    {
        "id": "math_g5_decimal_operations",
        "name": "Decimal Operations",
        "description": "Adding, subtracting, multiplying, and dividing decimals. Understanding decimal place alignment.",
        "domain": "Mathematics",
        "grade_level": 5,
        "difficulty": 0.6,
        "keywords": ["decimals", "operations", "addition", "subtraction", "multiplication"],
        "curriculum_code": "MATH.5.NBT.7",
        "estimated_time_minutes": 90
    },
    {
        "id": "math_g5_order_of_operations",
        "name": "Order of Operations",
        "description": "Understanding and applying the order of operations (PEMDAS/BODMAS) to evaluate expressions.",
        "domain": "Mathematics",
        "grade_level": 5,
        "difficulty": 0.6,
        "keywords": ["order of operations", "PEMDAS", "BODMAS", "expressions"],
        "curriculum_code": "MATH.5.OA.1",
        "estimated_time_minutes": 60
    },
    
    # --- MIDDLE SCHOOL (Grades 6-8) ---
    
    # Grade 6 - Ratios & Pre-Algebra
    {
        "id": "math_g6_ratios",
        "name": "Ratios and Proportions",
        "description": "Understanding ratio concepts and using ratio reasoning to solve problems.",
        "domain": "Mathematics",
        "grade_level": 6,
        "difficulty": 0.55,
        "keywords": ["ratio", "proportion", "rate", "unit rate"],
        "curriculum_code": "MATH.6.RP.1",
        "estimated_time_minutes": 75
    },
    {
        "id": "math_g6_percentages",
        "name": "Percentages",
        "description": "Understanding percentages as rates per 100. Converting between fractions, decimals, and percentages.",
        "domain": "Mathematics",
        "grade_level": 6,
        "difficulty": 0.6,
        "keywords": ["percentage", "percent", "convert", "fraction", "decimal"],
        "curriculum_code": "MATH.6.RP.3",
        "estimated_time_minutes": 90
    },
    {
        "id": "math_g6_negative_numbers",
        "name": "Negative Numbers",
        "description": "Understanding integers and rational numbers including negative numbers on the number line.",
        "domain": "Mathematics",
        "grade_level": 6,
        "difficulty": 0.6,
        "keywords": ["integers", "negative numbers", "number line", "absolute value"],
        "curriculum_code": "MATH.6.NS.5",
        "estimated_time_minutes": 60
    },
    {
        "id": "math_g6_variables",
        "name": "Variables and Expressions",
        "description": "Writing and evaluating numerical expressions with variables. Introduction to algebraic thinking.",
        "domain": "Mathematics",
        "grade_level": 6,
        "difficulty": 0.65,
        "keywords": ["variables", "expressions", "algebra", "evaluate"],
        "curriculum_code": "MATH.6.EE.1",
        "estimated_time_minutes": 75
    },
    
    # Grade 7 - Algebra Foundations
    {
        "id": "math_g7_operations_rational",
        "name": "Operations with Rational Numbers",
        "description": "Adding, subtracting, multiplying, and dividing rational numbers including fractions and decimals.",
        "domain": "Mathematics",
        "grade_level": 7,
        "difficulty": 0.65,
        "keywords": ["rational numbers", "operations", "fractions", "decimals", "integers"],
        "curriculum_code": "MATH.7.NS.1",
        "estimated_time_minutes": 90
    },
    {
        "id": "math_g7_equations_intro",
        "name": "Solving Linear Equations",
        "description": "Solving one-step and two-step linear equations. Understanding equality and inverse operations.",
        "domain": "Mathematics",
        "grade_level": 7,
        "difficulty": 0.7,
        "keywords": ["equations", "linear", "solve", "inverse operations", "variables"],
        "curriculum_code": "MATH.7.EE.4",
        "estimated_time_minutes": 120
    },
    {
        "id": "math_g7_proportional_relationships",
        "name": "Proportional Relationships",
        "description": "Understanding and representing proportional relationships between quantities.",
        "domain": "Mathematics",
        "grade_level": 7,
        "difficulty": 0.65,
        "keywords": ["proportional", "constant of proportionality", "graph", "table"],
        "curriculum_code": "MATH.7.RP.2",
        "estimated_time_minutes": 90
    },
    {
        "id": "math_g7_geometry_area",
        "name": "Area and Circumference",
        "description": "Calculating area and circumference of circles. Area of composite figures.",
        "domain": "Mathematics",
        "grade_level": 7,
        "difficulty": 0.6,
        "keywords": ["area", "circumference", "circle", "pi", "composite figures"],
        "curriculum_code": "MATH.7.G.4",
        "estimated_time_minutes": 75
    },
    
    # Grade 8 - Algebra I Foundations
    {
        "id": "math_g8_exponents",
        "name": "Exponents and Scientific Notation",
        "description": "Understanding and applying properties of integer exponents. Working with scientific notation.",
        "domain": "Mathematics",
        "grade_level": 8,
        "difficulty": 0.65,
        "keywords": ["exponents", "powers", "scientific notation", "properties"],
        "curriculum_code": "MATH.8.EE.1",
        "estimated_time_minutes": 90
    },
    {
        "id": "math_g8_linear_equations",
        "name": "Linear Equations and Graphs",
        "description": "Graphing linear equations. Understanding slope and y-intercept. Slope-intercept form.",
        "domain": "Mathematics",
        "grade_level": 8,
        "difficulty": 0.7,
        "keywords": ["linear equations", "slope", "y-intercept", "graph", "slope-intercept form"],
        "curriculum_code": "MATH.8.EE.5",
        "estimated_time_minutes": 120
    },
    {
        "id": "math_g8_systems_equations",
        "name": "Systems of Linear Equations",
        "description": "Solving systems of two linear equations. Graphical, substitution, and elimination methods.",
        "domain": "Mathematics",
        "grade_level": 8,
        "difficulty": 0.75,
        "keywords": ["systems", "linear equations", "substitution", "elimination", "intersection"],
        "curriculum_code": "MATH.8.EE.8",
        "estimated_time_minutes": 150
    },
    {
        "id": "math_g8_functions",
        "name": "Introduction to Functions",
        "description": "Understanding functions as inputs and outputs. Function notation and identifying functions.",
        "domain": "Mathematics",
        "grade_level": 8,
        "difficulty": 0.7,
        "keywords": ["functions", "input", "output", "domain", "range", "notation"],
        "curriculum_code": "MATH.8.F.1",
        "estimated_time_minutes": 90
    },
    {
        "id": "math_g8_pythagorean",
        "name": "Pythagorean Theorem",
        "description": "Understanding and applying the Pythagorean theorem to find missing sides in right triangles.",
        "domain": "Mathematics",
        "grade_level": 8,
        "difficulty": 0.65,
        "keywords": ["Pythagorean theorem", "right triangle", "hypotenuse", "legs"],
        "curriculum_code": "MATH.8.G.7",
        "estimated_time_minutes": 75
    },
    
    
    # Algebra I
    {
        "id": "math_hs_quadratic_equations",
        "name": "Quadratic Equations",
        "description": "Solving quadratic equations by factoring, completing the square, and quadratic formula.",
        "domain": "Mathematics",
        "grade_level": 9,
        "difficulty": 0.75,
        "keywords": ["quadratic", "factoring", "completing the square", "quadratic formula"],
        "curriculum_code": "MATH.A1.REI.4",
        "estimated_time_minutes": 180
    },
    {
        "id": "math_hs_polynomials",
        "name": "Polynomial Operations",
        "description": "Adding, subtracting, multiplying, and dividing polynomials. Factoring polynomials.",
        "domain": "Mathematics",
        "grade_level": 9,
        "difficulty": 0.7,
        "keywords": ["polynomials", "operations", "factoring", "degree"],
        "curriculum_code": "MATH.A1.APR.1",
        "estimated_time_minutes": 150
    },
    {
        "id": "math_hs_radicals",
        "name": "Radical Expressions and Equations",
        "description": "Simplifying radical expressions. Solving equations with radicals. Rational exponents.",
        "domain": "Mathematics",
        "grade_level": 9,
        "difficulty": 0.7,
        "keywords": ["radicals", "square root", "rational exponents", "simplify"],
        "curriculum_code": "MATH.A1.RN.1",
        "estimated_time_minutes": 120
    },
    
    # Geometry
    {
        "id": "math_hs_congruent_triangles",
        "name": "Congruent Triangles",
        "description": "Proving triangle congruence using SSS, SAS, ASA, AAS, and HL. CPCTC reasoning.",
        "domain": "Mathematics",
        "grade_level": 10,
        "difficulty": 0.7,
        "keywords": ["congruent", "triangles", "proof", "SSS", "SAS", "ASA", "CPCTC"],
        "curriculum_code": "MATH.G.CO.8",
        "estimated_time_minutes": 150
    },
    {
        "id": "math_hs_similar_triangles",
        "name": "Similar Triangles",
        "description": "Understanding similarity. Proving triangles similar using AA, SAS, and SSS similarity.",
        "domain": "Mathematics",
        "grade_level": 10,
        "difficulty": 0.7,
        "keywords": ["similar", "triangles", "proportion", "AA", "scale factor"],
        "curriculum_code": "MATH.G.SRT.2",
        "estimated_time_minutes": 120
    },
    {
        "id": "math_hs_trigonometry_intro",
        "name": "Introduction to Trigonometry",
        "description": "Understanding trigonometric ratios: sine, cosine, and tangent. SOH-CAH-TOA.",
        "domain": "Mathematics",
        "grade_level": 10,
        "difficulty": 0.75,
        "keywords": ["trigonometry", "sine", "cosine", "tangent", "SOH-CAH-TOA"],
        "curriculum_code": "MATH.G.SRT.6",
        "estimated_time_minutes": 150
    },
    
    # Algebra II
    {
        "id": "math_hs_rational_functions",
        "name": "Rational Functions",
        "description": "Graphing rational functions. Finding asymptotes, holes, and intercepts. Solving rational equations.",
        "domain": "Mathematics",
        "grade_level": 11,
        "difficulty": 0.8,
        "keywords": ["rational functions", "asymptotes", "domain", "holes"],
        "curriculum_code": "MATH.A2.APR.7",
        "estimated_time_minutes": 180
    },
    {
        "id": "math_hs_logarithms",
        "name": "Logarithms",
        "description": "Understanding logarithms as inverses of exponentials. Properties of logarithms. Solving logarithmic equations.",
        "domain": "Mathematics",
        "grade_level": 11,
        "difficulty": 0.8,
        "keywords": ["logarithms", "log", "exponential", "inverse", "properties"],
        "curriculum_code": "MATH.A2.F.LE.4",
        "estimated_time_minutes": 180
    },
    {
        "id": "math_hs_sequences_series",
        "name": "Sequences and Series",
        "description": "Arithmetic and geometric sequences and series. Sum formulas. Sigma notation.",
        "domain": "Mathematics",
        "grade_level": 11,
        "difficulty": 0.75,
        "keywords": ["sequences", "series", "arithmetic", "geometric", "sigma", "sum"],
        "curriculum_code": "MATH.A2.A.SSE.4",
        "estimated_time_minutes": 150
    },
    
    # Pre-Calculus / Calculus
    {
        "id": "math_hs_limits",
        "name": "Limits and Continuity",
        "description": "Understanding limits graphically and algebraically. Continuity of functions. Limit laws.",
        "domain": "Mathematics",
        "grade_level": 12,
        "difficulty": 0.85,
        "keywords": ["limits", "continuity", "approach", "infinity", "limit laws"],
        "curriculum_code": "MATH.CAL.LIM.1",
        "estimated_time_minutes": 180
    },
    {
        "id": "math_hs_derivatives",
        "name": "Derivatives",
        "description": "Understanding derivatives as rates of change. Differentiation rules. Applications of derivatives.",
        "domain": "Mathematics",
        "grade_level": 12,
        "difficulty": 0.9,
        "keywords": ["derivatives", "differentiation", "rate of change", "slope", "chain rule"],
        "curriculum_code": "MATH.CAL.DER.1",
        "estimated_time_minutes": 240
    },
    {
        "id": "math_hs_integrals",
        "name": "Integrals",
        "description": "Understanding integrals as area. Fundamental theorem of calculus. Integration techniques.",
        "domain": "Mathematics",
        "grade_level": 12,
        "difficulty": 0.9,
        "keywords": ["integrals", "integration", "area", "antiderivative", "fundamental theorem"],
        "curriculum_code": "MATH.CAL.INT.1",
        "estimated_time_minutes": 240
    },
    
    # --- ADDITIONAL DOMAIN: Physics ---
    {
        "id": "physics_motion",
        "name": "Kinematics: Motion in One Dimension",
        "description": "Understanding position, velocity, and acceleration. Equations of motion. Graphical analysis.",
        "domain": "Physics",
        "grade_level": 9,
        "difficulty": 0.6,
        "keywords": ["kinematics", "velocity", "acceleration", "motion", "displacement"],
        "curriculum_code": "PHYS.1.KIN",
        "estimated_time_minutes": 120
    },
    {
        "id": "physics_forces",
        "name": "Newton's Laws of Motion",
        "description": "Understanding forces, mass, and acceleration. Newton's three laws. Free-body diagrams.",
        "domain": "Physics",
        "grade_level": 9,
        "difficulty": 0.65,
        "keywords": ["Newton's laws", "force", "mass", "acceleration", "free-body diagram"],
        "curriculum_code": "PHYS.1.NWT",
        "estimated_time_minutes": 150
    },
    {
        "id": "physics_energy",
        "name": "Work, Energy, and Power",
        "description": "Understanding work, kinetic energy, potential energy, and power. Conservation of energy.",
        "domain": "Physics",
        "grade_level": 10,
        "difficulty": 0.7,
        "keywords": ["work", "energy", "power", "conservation", "kinetic", "potential"],
        "curriculum_code": "PHYS.1.ENR",
        "estimated_time_minutes": 150
    },
]




RELATIONSHIPS: List[Dict[str, Any]] = [

    {"source_id": "math_g1_addition_basic", "target_id": "math_g1_counting", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g1_subtraction_basic", "target_id": "math_g1_counting", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g1_subtraction_basic", "target_id": "math_g1_addition_basic", "relationship_type": "REQUIRES", "strength": 0.8},
    
    {"source_id": "math_g2_place_value", "target_id": "math_g1_counting", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g2_addition_two_digit", "target_id": "math_g1_addition_basic", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g2_addition_two_digit", "target_id": "math_g2_place_value", "relationship_type": "REQUIRES", "strength": 0.9},
    {"source_id": "math_g2_subtraction_two_digit", "target_id": "math_g1_subtraction_basic", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g2_subtraction_two_digit", "target_id": "math_g2_place_value", "relationship_type": "REQUIRES", "strength": 0.9},
    
    {"source_id": "math_g3_multiplication_intro", "target_id": "math_g2_addition_two_digit", "relationship_type": "REQUIRES", "strength": 0.9},
    {"source_id": "math_g3_division_intro", "target_id": "math_g3_multiplication_intro", "relationship_type": "REQUIRES", "strength": 0.9},
    {"source_id": "math_g3_division_intro", "target_id": "math_g2_subtraction_two_digit", "relationship_type": "REQUIRES", "strength": 0.7},
    {"source_id": "math_g3_fractions_intro", "target_id": "math_g2_place_value", "relationship_type": "REQUIRES", "strength": 0.6},
    {"source_id": "math_g3_fractions_intro", "target_id": "math_g3_division_intro", "relationship_type": "REQUIRES", "strength": 0.7},
    
    {"source_id": "math_g4_multi_digit_multiplication", "target_id": "math_g3_multiplication_intro", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g4_multi_digit_multiplication", "target_id": "math_g2_place_value", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_g4_long_division", "target_id": "math_g3_division_intro", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g4_long_division", "target_id": "math_g4_multi_digit_multiplication", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_g4_equivalent_fractions", "target_id": "math_g3_fractions_intro", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g4_equivalent_fractions", "target_id": "math_g3_multiplication_intro", "relationship_type": "REQUIRES", "strength": 0.7},
    
    {"source_id": "math_g5_decimals_intro", "target_id": "math_g2_place_value", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g5_decimals_intro", "target_id": "math_g4_equivalent_fractions", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_g5_decimal_operations", "target_id": "math_g5_decimals_intro", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g5_order_of_operations", "target_id": "math_g4_multi_digit_multiplication", "relationship_type": "REQUIRES", "strength": 0.7},
    
    {"source_id": "math_g6_ratios", "target_id": "math_g3_fractions_intro", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_g6_percentages", "target_id": "math_g6_ratios", "relationship_type": "REQUIRES", "strength": 0.9},
    {"source_id": "math_g6_percentages", "target_id": "math_g5_decimals_intro", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_g6_negative_numbers", "target_id": "math_g2_subtraction_two_digit", "relationship_type": "REQUIRES", "strength": 0.7},
    {"source_id": "math_g6_variables", "target_id": "math_g5_order_of_operations", "relationship_type": "REQUIRES", "strength": 0.8},
    
    {"source_id": "math_g7_operations_rational", "target_id": "math_g6_negative_numbers", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g7_operations_rational", "target_id": "math_g3_fractions_intro", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_g7_equations_intro", "target_id": "math_g6_variables", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g7_equations_intro", "target_id": "math_g7_operations_rational", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_g7_proportional_relationships", "target_id": "math_g6_ratios", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g7_geometry_area", "target_id": "math_g4_multi_digit_multiplication", "relationship_type": "REQUIRES", "strength": 0.6},
    
    {"source_id": "math_g8_exponents", "target_id": "math_g3_multiplication_intro", "relationship_type": "REQUIRES", "strength": 0.7},
    {"source_id": "math_g8_linear_equations", "target_id": "math_g7_equations_intro", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g8_linear_equations", "target_id": "math_g7_proportional_relationships", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_g8_systems_equations", "target_id": "math_g8_linear_equations", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_g8_functions", "target_id": "math_g8_linear_equations", "relationship_type": "REQUIRES", "strength": 0.9},
    {"source_id": "math_g8_pythagorean", "target_id": "math_g8_exponents", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_g8_pythagorean", "target_id": "math_g4_equivalent_fractions", "relationship_type": "REQUIRES", "strength": 0.5},
    
    {"source_id": "math_hs_quadratic_equations", "target_id": "math_g8_linear_equations", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_hs_quadratic_equations", "target_id": "math_g8_exponents", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_hs_polynomials", "target_id": "math_g8_exponents", "relationship_type": "REQUIRES", "strength": 0.9},
    {"source_id": "math_hs_polynomials", "target_id": "math_g8_linear_equations", "relationship_type": "REQUIRES", "strength": 0.7},
    {"source_id": "math_hs_radicals", "target_id": "math_g8_exponents", "relationship_type": "REQUIRES", "strength": 1.0},
    
    {"source_id": "math_hs_congruent_triangles", "target_id": "math_g8_pythagorean", "relationship_type": "REQUIRES", "strength": 0.6},
    {"source_id": "math_hs_similar_triangles", "target_id": "math_hs_congruent_triangles", "relationship_type": "REQUIRES", "strength": 0.7},
    {"source_id": "math_hs_similar_triangles", "target_id": "math_g7_proportional_relationships", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_hs_trigonometry_intro", "target_id": "math_hs_similar_triangles", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_hs_trigonometry_intro", "target_id": "math_g8_pythagorean", "relationship_type": "REQUIRES", "strength": 0.9},
  
    {"source_id": "math_hs_rational_functions", "target_id": "math_hs_polynomials", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_hs_rational_functions", "target_id": "math_g8_functions", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_hs_logarithms", "target_id": "math_g8_exponents", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_hs_logarithms", "target_id": "math_g8_functions", "relationship_type": "REQUIRES", "strength": 0.9},
    {"source_id": "math_hs_sequences_series", "target_id": "math_g8_functions", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_hs_sequences_series", "target_id": "math_g8_exponents", "relationship_type": "REQUIRES", "strength": 0.7},
    
    {"source_id": "math_hs_limits", "target_id": "math_g8_functions", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_hs_limits", "target_id": "math_hs_logarithms", "relationship_type": "REQUIRES", "strength": 0.7},
    {"source_id": "math_hs_derivatives", "target_id": "math_hs_limits", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "math_hs_derivatives", "target_id": "math_hs_quadratic_equations", "relationship_type": "REQUIRES", "strength": 0.8},
    {"source_id": "math_hs_integrals", "target_id": "math_hs_derivatives", "relationship_type": "REQUIRES", "strength": 1.0},
    
    {"source_id": "physics_motion", "target_id": "math_g8_linear_equations", "relationship_type": "REQUIRES", "strength": 0.9},
    {"source_id": "physics_forces", "target_id": "physics_motion", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "physics_forces", "target_id": "math_g8_systems_equations", "relationship_type": "REQUIRES", "strength": 0.7},
    {"source_id": "physics_energy", "target_id": "physics_forces", "relationship_type": "REQUIRES", "strength": 1.0},
    {"source_id": "physics_energy", "target_id": "math_hs_quadratic_equations", "relationship_type": "REQUIRES", "strength": 0.6},
    
    {"source_id": "math_g1_addition_basic", "target_id": "math_g1_counting", "relationship_type": "BUILDS_ON", "strength": 1.0},
    {"source_id": "math_g3_multiplication_intro", "target_id": "math_g2_addition_two_digit", "relationship_type": "BUILDS_ON", "strength": 0.9},
    {"source_id": "math_g8_linear_equations", "target_id": "math_g7_equations_intro", "relationship_type": "BUILDS_ON", "strength": 1.0},
    {"source_id": "math_hs_derivatives", "target_id": "math_hs_limits", "relationship_type": "BUILDS_ON", "strength": 1.0},
]


def get_all_concepts() -> List[Dict[str, Any]]:
    return CONCEPTS


def get_all_relationships() -> List[Dict[str, Any]]:
    return RELATIONSHIPS


def get_concepts_by_grade(grade_level: int) -> List[Dict[str, Any]]:
    return [c for c in CONCEPTS if c.get("grade_level") == grade_level]


def get_concepts_by_domain(domain: str) -> List[Dict[str, Any]]:
    return [c for c in CONCEPTS if c.get("domain") == domain]


def get_prerequisites_for_concept(concept_id: str) -> List[str]:
    return [
        r["target_id"] 
        for r in RELATIONSHIPS 
        if r["source_id"] == concept_id and r["relationship_type"] == "REQUIRES"
    ]

async def load_sample_curriculum(neo4j):
  

    queries = [

        """
        CREATE (:Concept {id:'limits', name:'Limits', domain:'Mathematics',
        description:'Understanding approaching values'})
        """,

        """
        CREATE (:Concept {id:'derivatives', name:'Derivatives', domain:'Mathematics',
        description:'Rate of change'})
        """,

        """
        CREATE (:Concept {id:'integration', name:'Integration', domain:'Mathematics',
        description:'Accumulation and area under curve'})
        """,

        """
        MATCH (a:Concept {id:'derivatives'}),(b:Concept {id:'limits'})
        CREATE (a)-[:REQUIRES]->(b)
        """,

        """
        MATCH (a:Concept {id:'integration'}),(b:Concept {id:'derivatives'})
        CREATE (a)-[:REQUIRES]->(b)
        """
    ]

    for q in queries:
        await neo4j.execute_query(q)

    return {"status": "Curriculum Loaded"}
