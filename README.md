# COMP3173 24F - Project Description

# **Prologue**

### **Project Title: Set Algebra Calculator**

## **Grouping:** 

Two students are in a group, no need to be in the same section. Once grouping is completed, students are not allowed to change their groups. Please follow the instruction in the email from Lily on Oct. 8 and complete grouping on **AUTOLAB**. Grouping is accomplished only if both two students in a group confirm. 

## **Objective:** 

In this project, you will develop create a small calculator for Set Algebra. This algebra is simplified, which only consists of integers, set of integers, predicates, integer operators, set operators, logical operators, and relational operators. This language is designed to be straightforward and simple, making it easier for you to implement. So, some features look wired. Please accept if you see any and consider them as intentional design choices. Before commencing work on the project, it is imperative that you thoroughly review this document. Note that is **long**. 

**The input** will be a source code file, which may include zero or multiple variable declarations (integer or set) and one single calculation expression. The calculator will then analyze the source code which is formulated in in Set Algebra. The analyzer should detect and highlight any errors presented in the source program; if no errors are found, the calculator will proceed with evaluation.

The first part of this document explains the language’s features with examples, which is like a programming language user manual. By reading it, students will gain a comprehensive understanding of the language, enable them to write expressions in this language and to identify errors in source code. The subsequent part of the document outlines the instructions of implementation by different phases. Students are expected to complete the project by sequentially completing these 3 phases.

## **Implementation Language:**

**C or Python**, you have your own choice. Startup codes and instructions for both languages are given in the package. 

## **Grading:**

- Submission – 5%
- Compilation – 5%
- Phase 1 – 40%
- Phase 2 – 30%
- Phase 3 typing – 10%
- Phase 3 evaluation – 10%
- Bonus 1 “simplify” without Distributive Law – 2%
- Bonus 2 “simplify” with Distributive Law – 2%
- Bonus 3 function or inequality order testing – 1%

## **DDL:**

We do not put DDLs for each phase. The DDL for the entire project will be **Dec. 17 midnight**, the last day of classes. But, **do not wait until the last minute**. Please expect that the project will cause **40 human hours**. Students will submit their works to **AUTOLAB**. (More instructions will be given later.) Marking will be purely based on testcases by AUTOLAB.

## **Testcases:**

More testcases will not be with this project description. Because students can check the correct outcome at [Set Algebra Playground](https://set-algebra.pages.dev/). **(**![img](file:///C:/Users/ASUS/AppData/Local/Temp/msohtmlclip1/01/clip_image002.gif)**Please try this!!!**) Students can also write their own testcases and understand the language better.

# **Language Feature**

The user manual of this language is listed.

### **Keywords**:

- “let”: initiates a variable declaration.
- “be”: acts as the assignment operator in other programming language.
- “int”: specifies the variable is of **integer type** during its declaration.
- “set”: specifies the variable is of **set type** during its declaration.
- “show”: acts as the main function in other programming languages, which initialize a calculation.



### **Data types**:

- **Integer**:
  - Basic data type
  - A single-digit integer is an arbitrary decimal number.
  - A multi-digit integer starts with a non-zero decimal number and followed by any sequence of arbitrary decimal numbers.
  - Users can only declare non-negative integers. Negative integers are constructed through subtraction operations.



- **Arithmetic expression**:

  - Constructed data type

  - Users are **not** allowed to **declare** an arithmetic expression. There is no specific data type keyword for arithmetic expressions in the language. This data type only exists in the compiler. You can also check the keywords. There is no data type keyword for arithmetic expressions.

  - An **atomic arithmetic expression** is either an integer constant or an integer variable.

  - A compound arithmetic expression consists of two arithmetic expressions connected by an arithmetic operator (addition “+”, subtraction “-”, multiplication “*”). And parentheses are used to define substructures within expression. For example, 
    $$
    1 + 2 – 3 * 4
    $$
    is parsed as: 
    $$
    ( 1 + 2 ) - ( 3 * 4 )
    $$



- **Predicates**

  - Constructed data type

  - Same as arithmetic expression, predicates are **not** directly **declared** by users but are instead managed within the compiler.

  - An **atomic predicate** is a relational comparison, which can be of two types:

    - **Integer value comparison**: involving the comparison of two integers using relational operator less than (“<”), greater than (“>”), or equality (“=”); or
    - **Membership testing**: used to determine if an element is a member of a set using the membership operator “@”. 

  - A **compound predicate** is formed by combining “smaller” predicates (either atomic or compound) using logical operators:

    - **Binary logical operators**: two (atomic or compound) predicates connected by a conjunction (“&”) or disjunction (“|”) 

    - **Unary logical operators**: Negation (“!”) which precedes another predicate.

      For example,
      $$
      P \& Q
      $$
      and
      $$
      ! R
      $$
      where P, Q, and R are predicates.

  - Parentheses are also used to define substructures in predicates. Parentheses are essential for defining the precedence and grouping of operations within predicates, ensuring the correct evaluation of complex expressions.



- **Bool**:

  - Basic data type

  - **Cannot** be declared by users

  - Has only two constants: “true” and “false”

  - A Boolean is produced by the evaluation on a predication without uninitialized variables. For example, 
    $$
    x > 5
    $$
    is a predicate if variable x has not been initialized. But if x has been initialized as 3 previously, then the predicate becomes 
    $$
    3 > 5
    $$
    and can be evaluated to be Boolean “false”. The behavior of “>” will be explained later in this document.



- **Set**:

  - Constructed data type

  - Can be declared by users

  - A set is defined in using this syntax within the language 
    $$
    { x : P(x) }
    $$
    where 

    - a set defnition is enclosed within curly braces “{ }”;
    -  “x” is a variable name called representative, whose scope is limited within **this** **set** definition;
    - “:” is another punctuation separating the representative x from the rest part of the definition; 
    - “P(x)” is a predicate that applies to the variable x, serving as the characteristic function of the set, which performs a logical test on x. If P(x) evaluates to **true**, then x is an element of the set; otherwise, x is not in the set.

  - This project focuses solely on sets of integers. Other types of sets, such as sets of strings, pairs, or sets of sets are not included. This limitation is intentional, aiming to simplify the implementation process. Goliath is trying to make your life easy!

- **Void**:
  - Basic data type
  - **Cannot** be declared by users
  - For subexpressions without any type 



### **Identifier**: 

arbitrary strings of English letters **in lower case** and are not reserved by keywords.



### **Operators**:

- **Arithmetic operators**:
  - “+”: integer addition, calculates the sum of two integers
  - “-”: integer subtraction, calculates the difference of two integers
  - “*”: integer multiplication, calculates the product of two integers
  - Multiplication has the highest precedence. Addition and subtraction have equal precedence, which is lower than multiplication. 



- **Relational operators (for integers)**:
  - “<” (Less Than): returns “true” if the left-hand side integer is **less than** the integer on the right-hand side
  - “>” (Greater Than): returns “true” if the integer on the left-hand side is **greater** than the integer on the right-hand side integer 
  - “=”: (Equal), returns “true” if the integer on the left-hand side is **equal** to the integer on the right-hand side integer



- **Relational operator (membership)**:
  - “@”: This operator checks if the element on the left-hand side is a member of the set on the right-hand side. It returns “true” if the element is **in** set, otherwise it returns “false”.



- **Logical operators**: 

  - conjunction “&”, disjunction “|”, and negation “!” are behaved as the following.

    **Truth Tables for Logical Operators:**

    Conjunction table

    |   &   | true  | false |
    | :---: | :---: | :---: |
    | true  | true  | false |
    | false | false | false |

    Disjunction table  

    |  \|   | true | false |
    | :---: | :--: | :---: |
    | true  | true | true  |
    | false | true | false |

    Negation table

    |  x   | true  | false |
    | :--: | :---: | :---: |
    |  !x  | false | true  |

  - Negation has the highest **precedence**, then conjunction, and then disjunction.



- **Set operators**:
  - “I”: set intersection, calculates the **intersection** of two sets 
  - “U”: set union, calculate the **union** of two sets
  - Intersection has a higher **precedence** than union.



### **Sentences**: 

- Each **source code** contains zero, one, or multiple **variable declaration(s)**; and **exactly one calculation expression**.

- Each **variable declaration** is in the following syntax
  $$
  let \ T \ id \ be\  E .
  $$
  where

  - T is a type name (either int or set), 
  - id is a variable identifier, 
  - E is an expression that assigns a value (a set definition is also a “value”, even it is not a number) of the specific type to the variable.
  - The period “.” Marks the end of the declaration.

  For example, 
  $$
  let \ int \ a \ be \ 5 .
  $$
  defines an integer a whose value is 5. And
  $$
  let \ set \ s \ be \ \{ x : x = 5 \} . 
  $$
  defines a set s which contains only one integer 5.

- A **calculation expression** starts with keyword “show” and followed by an **algebraic expression**, which can be an arithmetic expression, a Boolean expression (a predicate with all variables initialized), or a set algebra expression. A calculation expression is also ended by a full stop “.”. For example,
  - To calculates the union of sets S1 and S2: $show \ S1 \ U \ S2 .$
  - To calculates the sum of integers 1 and 2: $show \ 1 \ + \ 2 .$
  -  To test if integer 3 in S1 or not: $show \ 3 \ @ \ S1 .$

  **Output**: After the calculation, the program prints the outcome on the screen (type and value). (see the examples below). For set operators, the “show” statement does not simplify the characteristic function. For example,
  $$
  show \ \{ x : x > 3 \} \cup  \{ x : x > 5 \} .
  $$
  will output
  $$
  \{ x : ( x > 3 ) \mid  ( x > 5 ) \}
  $$
  rather than 
  $$
  \{ x : x > 3 \}
  $$
  even though the two sets are equivalent. This requirement will make this project easy. The simplification of predicates is an advanced feature and will be a bonus and explained later.

 

# **Phase 1 – Lexical Analysis**

**Timeline:** Students can start working on Phase 1 after “Lecture 3 – Finite Automata”.

**Description:**

In the first phase, students need to implement a lexer for this project. The lexer reads the source code as a stream of characters, cuts them into lexemes, classifies lexemes as tokens, and decides attributes for some lexemes. The lexer also reports lexical error (spelling mistakes) if the source code contains any. Tokens are previously defined in the language user manual and summarized again as below. The tokens that contain exactly one lexeme each are

- Keywords: let, be, show, int, set
- Punctuations: . , (, ) , {, }, :
- Arithmetic operators: +, -, *
- Relational operators: @, <, >
- Logic operators: &, |, !
- Set operators: U, I

And the tokens that contain infinite lexemes are

- Integer constant: num
- Variable names: id

The space symbol “ ” is a special character, which is ignored by the lexer but terminates other lexemes by force. For example,

- “let be” is recognized as two tokens “let” and “be”, because the space symbol terminates the lexeme “let”.
- “letbe” is recognized as one token “id”, because it is a string of lower English letters but not a keyword.
- “be123+a” is recognized as four tokens “be”, “num”, “+”, and “id”. 

**Symbol table** also needs to be implemented in this phase. It holds all variable names (ids) declared by users. Each variable name has another two attributes:

- the type of the variable (either “int” or “set”);
- the value of the variable. 

Note that the value for a set variable is not a number, but a set definition. For example “let set s be { x : x = 5 }”, the value of “s” is “{ x : x = 5 }”. But in Phase 1, a lexer cannot decide a value for a set.

The lexer is operated as the function call “next_token()” by the parser. It reads a few characters from the input and returns the first recognized token.

- If the token is an integer constant num, the function also returns its value. 
- If the token is a variable name id, the function stores this variable name in a symbol table and returns the variable location in the symbol table (for example a point in C language). 
- For other tokens, the function only returns the token name. 

# **Phase 2 – Syntax Analysis**

——————等待更新——————
