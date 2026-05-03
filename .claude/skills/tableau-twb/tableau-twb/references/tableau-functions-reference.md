# Tableau Functions Reference

A comprehensive reference of all functions available in Tableau calculated fields.

---

## Table of Contents

1. [Number Functions](#number-functions)
2. [String Functions](#string-functions)
3. [Date Functions](#date-functions)
4. [Type Conversion Functions](#type-conversion-functions)
5. [Logical Functions](#logical-functions)
6. [Aggregate Functions](#aggregate-functions)
7. [Table Calculation Functions](#table-calculation-functions)
8. [LOD (Level of Detail) Expressions](#lod-level-of-detail-expressions)
9. [Spatial Functions](#spatial-functions)
10. [User Functions](#user-functions)
11. [Pass-Through Functions (RAWSQL)](#pass-through-functions-rawsql)

---

## Number Functions

### ABS
Returns the absolute value of a number.
```
ABS(number)
```
Example: `ABS(-7)` → `7`

### ACOS
Returns the arc cosine of a number (in radians).
```
ACOS(number)
```
Example: `ACOS(0)` → `1.5707963267949` (π/2)

### ASIN
Returns the arc sine of a number (in radians).
```
ASIN(number)
```
Example: `ASIN(1)` → `1.5707963267949` (π/2)

### ATAN
Returns the arc tangent of a number (in radians).
```
ATAN(number)
```
Example: `ATAN(1)` → `0.785398163397448` (π/4)

### ATAN2
Returns the arc tangent of two numbers (y and x) in radians.
```
ATAN2(y, x)
```
Example: `ATAN2(1, 1)` → `0.785398163397448` (π/4)

### CEILING
Rounds a number to the nearest integer of equal or greater value.
```
CEILING(number)
```
Example: `CEILING(2.1)` → `3`

### COS
Returns the cosine of an angle (in radians).
```
COS(number)
```
Example: `COS(0)` → `1`

### COT
Returns the cotangent of an angle (in radians).
```
COT(number)
```
Example: `COT(PI()/4)` → `1`

### DEGREES
Converts radians to degrees.
```
DEGREES(number)
```
Example: `DEGREES(PI())` → `180`

### DIV
Returns the integer portion of a division.
```
DIV(integer1, integer2)
```
Example: `DIV(7, 2)` → `3`

### EXP
Returns e raised to the power of a given number.
```
EXP(number)
```
Example: `EXP(1)` → `2.71828182845905`

### FLOOR
Rounds a number to the nearest integer of equal or lesser value.
```
FLOOR(number)
```
Example: `FLOOR(2.9)` → `2`

### HEXBINX
Maps an x, y coordinate to the x-coordinate of the nearest hexagonal bin.
```
HEXBINX(x, y)
```

### HEXBINY
Maps an x, y coordinate to the y-coordinate of the nearest hexagonal bin.
```
HEXBINY(x, y)
```

### LN
Returns the natural logarithm of a number.
```
LN(number)
```
Example: `LN(EXP(1))` → `1`

### LOG
Returns the logarithm of a number for the given base. If the base is omitted, base 10 is used.
```
LOG(number [, base])
```
Example: `LOG(100)` → `2`
Example: `LOG(256, 2)` → `8`

### MAX (Number)
Returns the maximum of two arguments (must be the same type).
```
MAX(a, b)
```
Example: `MAX(4, 7)` → `7`

### MIN (Number)
Returns the minimum of two arguments (must be the same type).
```
MIN(a, b)
```
Example: `MIN(4, 7)` → `4`

### PI
Returns the numeric constant π (3.14159265358979).
```
PI()
```

### POWER
Raises a number to the specified power. Same as the `^` operator.
```
POWER(number, power)
```
Example: `POWER(2, 10)` → `1024`

### RADIANS
Converts degrees to radians.
```
RADIANS(number)
```
Example: `RADIANS(180)` → `3.14159265358979`

### ROUND
Rounds a number to a specified number of decimal places.
```
ROUND(number, [decimals])
```
Example: `ROUND(3.14159, 2)` → `3.14`

### SIGN
Returns the sign of a number: -1, 0, or 1.
```
SIGN(number)
```
Example: `SIGN(-7)` → `-1`

### SIN
Returns the sine of an angle (in radians).
```
SIN(number)
```
Example: `SIN(PI()/2)` → `1`

### SQRT
Returns the square root of a number.
```
SQRT(number)
```
Example: `SQRT(25)` → `5`

### SQUARE
Returns the square of a number.
```
SQUARE(number)
```
Example: `SQUARE(5)` → `25`

### TAN
Returns the tangent of an angle (in radians).
```
TAN(number)
```
Example: `TAN(PI()/4)` → `1`

### ZN
Returns the expression if it is not null; otherwise returns zero. Use to replace null values with zero.
```
ZN(expression)
```
Example: `ZN([Profit])` → `0` if Profit is null

---

## String Functions

### ASCII
Returns the ASCII code of the first character of a string.
```
ASCII(string)
```
Example: `ASCII("A")` → `65`

### CHAR
Returns the character encoded by the ASCII code.
```
CHAR(number)
```
Example: `CHAR(65)` → `"A"`

### CONTAINS
Returns true if the string contains the specified substring.
```
CONTAINS(string, substring)
```
Example: `CONTAINS("Tableau", "Tab")` → `TRUE`

### ENDSWITH
Returns true if the string ends with the specified substring.
```
ENDSWITH(string, substring)
```
Example: `ENDSWITH("Tableau", "leau")` → `TRUE`

### FIND
Returns the index position of the substring in the string, or 0 if not found. Optional start position.
```
FIND(string, substring, [start])
```
Example: `FIND("Tableau", "leau")` → `4`

### FINDNTH
Returns the position of the nth occurrence of a substring within a string.
```
FINDNTH(string, substring, occurrence)
```
Example: `FINDNTH("Tableau Software", "a", 2)` → `6`

### LEFT
Returns the leftmost number of characters from a string.
```
LEFT(string, number)
```
Example: `LEFT("Tableau", 3)` → `"Tab"`

### LEN
Returns the length of a string.
```
LEN(string)
```
Example: `LEN("Tableau")` → `7`

### LOWER
Converts a string to all lowercase.
```
LOWER(string)
```
Example: `LOWER("Tableau")` → `"tableau"`

### LTRIM
Returns the string with leading spaces removed.
```
LTRIM(string)
```
Example: `LTRIM("  Tableau")` → `"Tableau"`

### MAX (String)
Returns the maximum of two string arguments.
```
MAX(a, b)
```
Example: `MAX("banana", "apple")` → `"banana"`

### MID
Returns a substring starting at the given position for the given length.
```
MID(string, start, length)
```
Example: `MID("Tableau", 4, 4)` → `"leau"`

### MIN (String)
Returns the minimum of two string arguments.
```
MIN(a, b)
```
Example: `MIN("banana", "apple")` → `"apple"`

### REGEXP_EXTRACT
Returns the portion of the string matching the regular expression pattern. Use groups to return a substring.
```
REGEXP_EXTRACT(string, pattern)
```
Example: `REGEXP_EXTRACT("abc123", '(\d+)')` → `"123"`

### REGEXP_EXTRACT_NTH
Returns the nth capturing group from the regular expression match.
```
REGEXP_EXTRACT_NTH(string, pattern, index)
```
Example: `REGEXP_EXTRACT_NTH("abc-123-def", '(\w+)-(\d+)-(\w+)', 2)` → `"123"`

### REGEXP_MATCH
Returns true if the string matches the regular expression pattern.
```
REGEXP_MATCH(string, pattern)
```
Example: `REGEXP_MATCH("abc123", '\d+')` → `TRUE`

### REGEXP_REPLACE
Returns a string where substrings matching the regular expression pattern are replaced by the replacement string.
```
REGEXP_REPLACE(string, pattern, replacement)
```
Example: `REGEXP_REPLACE("abc 123", '\s', '-')` → `"abc-123"`

### REPLACE
Searches for a substring within a string, then replaces it. Uses position and length, not search text.
```
REPLACE(string, position, length, replacement)
```
Example: `REPLACE("Tableau", 1, 3, "Big")` → `"Bigleau"`

### RIGHT
Returns the rightmost number of characters from a string.
```
RIGHT(string, number)
```
Example: `RIGHT("Tableau", 4)` → `"leau"`

### RTRIM
Returns the string with trailing spaces removed.
```
RTRIM(string)
```
Example: `RTRIM("Tableau   ")` → `"Tableau"`

### SPACE
Returns a string composed of the specified number of spaces.
```
SPACE(number)
```
Example: `SPACE(3)` → `"   "`

### SPLIT
Returns a substring from a string using a delimiter and token number.
```
SPLIT(string, delimiter, token_number)
```
Example: `SPLIT("a-b-c", "-", 2)` → `"b"`

### STARTSWITH
Returns true if the string starts with the specified substring.
```
STARTSWITH(string, substring)
```
Example: `STARTSWITH("Tableau", "Tab")` → `TRUE`

### TRIM
Returns the string with leading and trailing spaces removed.
```
TRIM(string)
```
Example: `TRIM("  Tableau  ")` → `"Tableau"`

### UPPER
Converts a string to all uppercase.
```
UPPER(string)
```
Example: `UPPER("Tableau")` → `"TABLEAU"`

---

## Date Functions

### DATEADD
Adds an interval to a date and returns the new date.
```
DATEADD(date_part, interval, date)
```
Example: `DATEADD('month', 3, #2024-01-15#)` → `2024-04-15`

### DATEDIFF
Returns the difference between two dates in the specified date_part units.
```
DATEDIFF(date_part, date1, date2, [start_of_week])
```
Example: `DATEDIFF('day', #2024-01-01#, #2024-03-01#)` → `60`

### DATENAME
Returns a string representation of the specified date_part.
```
DATENAME(date_part, date, [start_of_week])
```
Example: `DATENAME('month', #2024-03-15#)` → `"March"`

### DATEPARSE
Converts a string to a datetime using the specified format.
```
DATEPARSE(format, string)
```
Example: `DATEPARSE("dd.MM.yyyy", "15.03.2024")` → `2024-03-15`

### DATEPART
Returns the specified part of a date as an integer.
```
DATEPART(date_part, date, [start_of_week])
```
Example: `DATEPART('year', #2024-03-15#)` → `2024`

### DATETRUNC
Truncates a date to the accuracy specified by the date_part.
```
DATETRUNC(date_part, date, [start_of_week])
```
Example: `DATETRUNC('month', #2024-03-15#)` → `2024-03-01`

### DAY
Returns the day of the month as an integer (1–31).
```
DAY(date)
```
Example: `DAY(#2024-03-15#)` → `15`

### ISDATE
Returns true if a given string is a valid date.
```
ISDATE(string)
```
Example: `ISDATE("2024-03-15")` → `TRUE`

### ISOQUARTER
Returns the ISO 8601 quarter of a date as an integer.
```
ISOQUARTER(date)
```

### ISOWEEK
Returns the ISO 8601 week of the year.
```
ISOWEEK(date)
```

### ISOWEEKDAY
Returns the ISO 8601 weekday (1=Monday through 7=Sunday).
```
ISOWEEKDAY(date)
```

### ISOYEAR
Returns the ISO 8601 year for a given date.
```
ISOYEAR(date)
```

### MAKEDATE
Returns a date value constructed from the given year, month, and day.
```
MAKEDATE(year, month, day)
```
Example: `MAKEDATE(2024, 3, 15)` → `2024-03-15`

### MAKEDATETIME
Returns a datetime from a date and a time.
```
MAKEDATETIME(date, time)
```
Example: `MAKEDATETIME(#2024-03-15#, #14:30:00#)`

### MAKETIME
Returns a time value from the given hour, minute, and second.
```
MAKETIME(hour, minute, second)
```
Example: `MAKETIME(14, 30, 0)` → `14:30:00`

### MAX (Date)
Returns the maximum (later) of two dates.
```
MAX(date1, date2)
```

### MIN (Date)
Returns the minimum (earlier) of two dates.
```
MIN(date1, date2)
```

### MONTH
Returns the month of a date as an integer (1–12).
```
MONTH(date)
```
Example: `MONTH(#2024-03-15#)` → `3`

### NOW
Returns the current date and time.
```
NOW()
```

### TODAY
Returns the current date.
```
TODAY()
```

### QUARTER
Returns the quarter of a date as an integer (1–4).
```
QUARTER(date)
```
Example: `QUARTER(#2024-03-15#)` → `1`

### WEEK
Returns the week number of a date as an integer.
```
WEEK(date)
```

### YEAR
Returns the year of a date as an integer.
```
YEAR(date)
```
Example: `YEAR(#2024-03-15#)` → `2024`

### Date Part Values

Use these string values for the `date_part` parameter:

| Date Part | Values |
|-----------|--------|
| Year | `'year'` |
| Quarter | `'quarter'` |
| Month | `'month'` |
| Week | `'week'` |
| Day | `'day'` |
| Hour | `'hour'` |
| Minute | `'minute'` |
| Second | `'second'` |
| ISO Year | `'iso-year'` |
| ISO Quarter | `'iso-quarter'` |
| ISO Week | `'iso-week'` |
| Day of Week | `'weekday'` |

---

## Type Conversion Functions

### DATE
Converts a string, number, or datetime to a date.
```
DATE(expression)
```
Example: `DATE("2024-03-15")` → `2024-03-15`

### DATETIME
Converts a string, number, or date to a datetime.
```
DATETIME(expression)
```
Example: `DATETIME("2024-03-15 14:30:00")`

### FLOAT
Converts an expression to a floating-point number.
```
FLOAT(expression)
```
Example: `FLOAT("3.14")` → `3.14`

### INT
Converts an expression to an integer (rounds toward zero).
```
INT(expression)
```
Example: `INT(8.9)` → `8`
Example: `INT(-8.9)` → `-8`

### STR
Converts an expression to a string.
```
STR(expression)
```
Example: `STR(42)` → `"42"`

---

## Logical Functions

### AND
Performs a logical conjunction on two expressions.
```
expression1 AND expression2
```
Example: `[Sales] > 1000 AND [Region] = "East"`

### CASE
Performs logical tests and returns the appropriate value. Similar to a switch statement.
```
CASE expression
  WHEN value1 THEN result1
  WHEN value2 THEN result2
  ...
  ELSE default_result
END
```
Example:
```
CASE [Region]
  WHEN "East" THEN 1
  WHEN "West" THEN 2
  ELSE 3
END
```

### ELSE
Used with IF and CASE expressions to define a default value.
```
IF condition THEN result ELSE default END
```

### ELSEIF
Used with IF to test additional conditions.
```
IF condition1 THEN result1
ELSEIF condition2 THEN result2
ELSE default
END
```

### END
Terminates an IF or CASE expression.

### IF
Performs a logical test and returns the appropriate value.
```
IF condition THEN result
[ELSEIF condition2 THEN result2]
[ELSE default]
END
```
Example:
```
IF [Profit] > 0 THEN "Profitable"
ELSEIF [Profit] = 0 THEN "Break Even"
ELSE "Loss"
END
```

### IFNULL
Returns the expression if it is not null; otherwise returns the alternate value.
```
IFNULL(expression, alternate_value)
```
Example: `IFNULL([Profit], 0)` → `0` if Profit is null

### IIF
Returns one value if a condition is true, another if false, and optionally a third if null.
```
IIF(condition, then, else, [unknown])
```
Example: `IIF([Sales] > 1000, "High", "Low")`

### IN
Checks whether a value matches any value in a list.
```
expression IN (value1, value2, ...)
```
Example: `[Region] IN ("East", "West")`

### ISFULLJOIN
Returns true if the current row is from a full outer join and has nulls from both sides.
```
ISFULLJOIN()
```

### ISMEMBEROF
Returns true if the current user is a member of the given group.
```
ISMEMBEROF(string)
```

### ISNULL
Returns true if the expression is null.
```
ISNULL(expression)
```
Example: `ISNULL([Discount])` → `TRUE` if Discount is null

### NOT
Performs a logical negation.
```
NOT expression
```
Example: `NOT [Returned]`

### OR
Performs a logical disjunction.
```
expression1 OR expression2
```
Example: `[Region] = "East" OR [Region] = "West"`

### THEN
Used with IF and CASE to define return values.

### WHEN
Used with CASE to define specific match values.

---

## Aggregate Functions

### ATTR
Returns the value of the expression if it has a single value for all rows; otherwise returns `*`.
```
ATTR(expression)
```

### AVG
Returns the average of all values in the expression. Ignores nulls.
```
AVG(expression)
```
Example: `AVG([Sales])`

### COLLECT
Returns an aggregate of combined spatial values.
```
COLLECT(spatial)
```

### CORR
Returns the Pearson correlation coefficient of two expressions.
```
CORR(expression1, expression2)
```

### COUNT
Returns the number of items in a group. Null values are not counted.
```
COUNT(expression)
```
Example: `COUNT([Order ID])`

### COUNTD
Returns the number of distinct items in a group. Null values are not counted.
```
COUNTD(expression)
```
Example: `COUNTD([Customer ID])`

### COVAR
Returns the sample covariance of two expressions.
```
COVAR(expression1, expression2)
```

### COVARP
Returns the population covariance of two expressions.
```
COVARP(expression1, expression2)
```

### MAX (Aggregate)
Returns the maximum value across all rows. Ignores nulls.
```
MAX(expression)
```
Example: `MAX([Sales])`

### MEDIAN
Returns the median value of an expression across all rows. Ignores nulls.
```
MEDIAN(expression)
```
Example: `MEDIAN([Sales])`

### MIN (Aggregate)
Returns the minimum value across all rows. Ignores nulls.
```
MIN(expression)
```
Example: `MIN([Sales])`

### PERCENTILE
Returns the percentile value at the specified mark.
```
PERCENTILE(expression, number)
```
Example: `PERCENTILE([Sales], 0.9)` → 90th percentile of Sales

### STDEV
Returns the sample standard deviation of the expression.
```
STDEV(expression)
```

### STDEVP
Returns the population standard deviation of the expression.
```
STDEVP(expression)
```

### SUM
Returns the sum of all values in the expression. Ignores nulls.
```
SUM(expression)
```
Example: `SUM([Sales])`

### VAR
Returns the sample variance of the expression.
```
VAR(expression)
```

### VARP
Returns the population variance of the expression.
```
VARP(expression)
```

---

## Table Calculation Functions

### FIRST
Returns the number of rows from the current row to the first row in the partition.
```
FIRST()
```
Example: At the 3rd row → `FIRST()` = `-2`

### INDEX
Returns the index of the current row in the partition.
```
INDEX()
```
Example: At the 3rd row → `INDEX()` = `3`

### LAST
Returns the number of rows from the current row to the last row in the partition.
```
LAST()
```
Example: At the 3rd of 5 rows → `LAST()` = `2`

### LOOKUP
Returns the value of the expression in a target row, specified as a relative offset from the current row.
```
LOOKUP(expression, [offset])
```
Example: `LOOKUP(SUM([Sales]), -1)` → SUM of Sales in the previous row

### MODEL_EXTENSION_BOOL
Returns the boolean result of an expression evaluated by a named TabPy or Analytics Extension model.
```
MODEL_EXTENSION_BOOL(model_name, arguments...)
```

### MODEL_EXTENSION_INT
Returns the integer result of an expression evaluated by a named model.
```
MODEL_EXTENSION_INT(model_name, arguments...)
```

### MODEL_EXTENSION_REAL
Returns the real (float) result of an expression evaluated by a named model.
```
MODEL_EXTENSION_REAL(model_name, arguments...)
```

### MODEL_EXTENSION_STR
Returns the string result of an expression evaluated by a named model.
```
MODEL_EXTENSION_STR(model_name, arguments...)
```

### MODEL_PERCENTILE
Returns the probability (0 to 1) that the expected value is less than or equal to the observed mark.
```
MODEL_PERCENTILE(target_expression, predictor_expression(s))
```

### MODEL_QUANTILE
Returns the target numeric value at the specified quantile given the predictor values.
```
MODEL_QUANTILE(quantile, target_expression, predictor_expression(s))
```

### PREVIOUS_VALUE
Returns the value of the expression on the previous row. Returns the given value on the first row.
```
PREVIOUS_VALUE(expression)
```
Example: `PREVIOUS_VALUE(0) + SUM([Sales])` → running total

### RANK
Returns the standard competition rank of the current row within the partition.
```
RANK(expression, ['asc' | 'desc'])
```
Example: `RANK(SUM([Sales]))` → ranks by Sales descending

### RANK_DENSE
Returns the dense rank (no gaps) of the current row within the partition.
```
RANK_DENSE(expression, ['asc' | 'desc'])
```

### RANK_MODIFIED
Returns the modified competition rank of the current row.
```
RANK_MODIFIED(expression, ['asc' | 'desc'])
```

### RANK_PERCENTILE
Returns the percentile rank (0 to 1) of the current row.
```
RANK_PERCENTILE(expression, ['asc' | 'desc'])
```

### RANK_UNIQUE
Returns a unique rank (no ties) of the current row.
```
RANK_UNIQUE(expression, ['asc' | 'desc'])
```

### RUNNING_AVG
Returns the running average of the expression from the first row to the current row.
```
RUNNING_AVG(expression)
```
Example: `RUNNING_AVG(SUM([Sales]))`

### RUNNING_COUNT
Returns the running count of the expression from the first row to the current row.
```
RUNNING_COUNT(expression)
```

### RUNNING_MAX
Returns the running maximum of the expression from the first row to the current row.
```
RUNNING_MAX(expression)
```

### RUNNING_MIN
Returns the running minimum of the expression from the first row to the current row.
```
RUNNING_MIN(expression)
```

### RUNNING_SUM
Returns the running sum of the expression from the first row to the current row.
```
RUNNING_SUM(expression)
```
Example: `RUNNING_SUM(SUM([Sales]))` → cumulative Sales

### SIZE
Returns the number of rows in the partition.
```
SIZE()
```

### SCRIPT_BOOL
Returns a boolean result from a TabPy / R / external analytics script.
```
SCRIPT_BOOL(script, expression, ...)
```

### SCRIPT_INT
Returns an integer result from an external analytics script.
```
SCRIPT_INT(script, expression, ...)
```

### SCRIPT_REAL
Returns a real number result from an external analytics script.
```
SCRIPT_REAL(script, expression, ...)
```

### SCRIPT_STR
Returns a string result from an external analytics script.
```
SCRIPT_STR(script, expression, ...)
```

### TOTAL
Returns the total for the given expression across the entire partition.
```
TOTAL(expression)
```
Example: `SUM([Sales]) / TOTAL(SUM([Sales]))` → percent of total

### WINDOW_AVG
Returns the average of the expression within the window.
```
WINDOW_AVG(expression, [start, end])
```
Example: `WINDOW_AVG(SUM([Sales]), -2, 0)` → 3-row moving average

### WINDOW_CORR
Returns the Pearson correlation coefficient within the window.
```
WINDOW_CORR(expression1, expression2, [start, end])
```

### WINDOW_COUNT
Returns the count of the expression within the window.
```
WINDOW_COUNT(expression, [start, end])
```

### WINDOW_COVAR
Returns the sample covariance within the window.
```
WINDOW_COVAR(expression1, expression2, [start, end])
```

### WINDOW_COVARP
Returns the population covariance within the window.
```
WINDOW_COVARP(expression1, expression2, [start, end])
```

### WINDOW_MAX
Returns the maximum of the expression within the window.
```
WINDOW_MAX(expression, [start, end])
```

### WINDOW_MEDIAN
Returns the median of the expression within the window.
```
WINDOW_MEDIAN(expression, [start, end])
```

### WINDOW_MIN
Returns the minimum of the expression within the window.
```
WINDOW_MIN(expression, [start, end])
```

### WINDOW_PERCENTILE
Returns the percentile value within the window.
```
WINDOW_PERCENTILE(expression, number, [start, end])
```

### WINDOW_STDEV
Returns the sample standard deviation within the window.
```
WINDOW_STDEV(expression, [start, end])
```

### WINDOW_STDEVP
Returns the population standard deviation within the window.
```
WINDOW_STDEVP(expression, [start, end])
```

### WINDOW_SUM
Returns the sum of the expression within the window.
```
WINDOW_SUM(expression, [start, end])
```
Example: `WINDOW_SUM(SUM([Sales]), -2, 0)` → 3-row moving sum

### WINDOW_VAR
Returns the sample variance within the window.
```
WINDOW_VAR(expression, [start, end])
```

### WINDOW_VARP
Returns the population variance within the window.
```
WINDOW_VARP(expression, [start, end])
```

---

## LOD (Level of Detail) Expressions

### FIXED
Computes the aggregate expression at the specified dimension level, regardless of the view.
```
{ FIXED [dimension1], [dimension2], ... : aggregate_expression }
```
Example: `{ FIXED [Customer ID] : SUM([Sales]) }` → total Sales per customer

### INCLUDE
Computes using the dimensions in the view PLUS the specified dimension(s).
```
{ INCLUDE [dimension] : aggregate_expression }
```
Example: `{ INCLUDE [Order ID] : SUM([Sales]) }` → adds Order ID to the level of detail

### EXCLUDE
Computes using the dimensions in the view MINUS the specified dimension(s).
```
{ EXCLUDE [Region] : SUM([Sales]) }
```
Example: Calculates SUM of Sales at a level that excludes Region from the view dimensions

### Table-Scoped LOD
A FIXED expression with no dimensions computes at the entire table level.
```
{ FIXED : SUM([Sales]) }
```
Example: Returns the grand total Sales across the entire data source

---

## Spatial Functions

### AREA
Returns the area of a spatial polygon.
```
AREA(spatial, 'units')
```
Units: `'meters'`, `'kilometers'`, `'miles'`, `'feet'`

### BUFFER
Returns a spatial polygon that is a buffer around the geometry.
```
BUFFER(spatial, distance, 'units')
```

### DISTANCE
Returns the distance between two spatial points.
```
DISTANCE(spatial_point1, spatial_point2, 'units')
```
Example: `DISTANCE([Origin], [Destination], 'miles')`

### INTERSECTS
Returns true if two spatial objects intersect.
```
INTERSECTS(spatial1, spatial2)
```

### LENGTH
Returns the length (perimeter) of a spatial object.
```
LENGTH(spatial, 'units')
```

### MAKEPOINT
Creates a spatial point from latitude and longitude.
```
MAKEPOINT(latitude, longitude)
```
Example: `MAKEPOINT([Lat], [Lon])`

### MAKELINE
Creates a spatial line between two points.
```
MAKELINE(spatial_point1, spatial_point2)
```
Example: `MAKELINE(MAKEPOINT(40.7, -74.0), MAKEPOINT(34.0, -118.2))`

### OUTLINE
Returns the boundary of a spatial polygon as a line.
```
OUTLINE(spatial)
```

### SHAPETYPE
Returns the type of a spatial object as a string.
```
SHAPETYPE(spatial)
```

---

## User Functions

### FULLNAME
Returns the full name of the current Tableau Server or Tableau Cloud user.
```
FULLNAME()
```

### ISFULLNAME
Returns true if the current user's full name matches the specified string.
```
ISFULLNAME(string)
```

### ISMEMBEROF
Returns true if the current user is a member of the specified group.
```
ISMEMBEROF(string)
```
Example: `ISMEMBEROF("Finance Team")`

### ISUSERNAME
Returns true if the current user's username matches the specified string.
```
ISUSERNAME(string)
```

### USERDOMAIN
Returns the domain of the current user (Windows authentication).
```
USERDOMAIN()
```

### USERNAME
Returns the username of the current Tableau Server or Tableau Cloud user.
```
USERNAME()
```

---

## Pass-Through Functions (RAWSQL)

These functions pass SQL directly to the underlying database. Availability depends on the data source.

### RAWSQL_BOOL
Returns a boolean from a raw SQL expression.
```
RAWSQL_BOOL("sql_expression", [field1], ...)
```
Example: `RAWSQL_BOOL("IS_ACTIVE(%1)", [Customer ID])`

### RAWSQL_DATE
Returns a date from a raw SQL expression.
```
RAWSQL_DATE("sql_expression", [field1], ...)
```

### RAWSQL_DATETIME
Returns a datetime from a raw SQL expression.
```
RAWSQL_DATETIME("sql_expression", [field1], ...)
```

### RAWSQL_INT
Returns an integer from a raw SQL expression.
```
RAWSQL_INT("sql_expression", [field1], ...)
```

### RAWSQL_REAL
Returns a float from a raw SQL expression.
```
RAWSQL_REAL("sql_expression", [field1], ...)
```

### RAWSQL_SPATIAL
Returns a spatial object from a raw SQL expression.
```
RAWSQL_SPATIAL("sql_expression", [field1], ...)
```

### RAWSQL_STR
Returns a string from a raw SQL expression.
```
RAWSQL_STR("sql_expression", [field1], ...)
```

---

> **Note:** Function availability may vary by data source. Some functions are not supported in all database connections. Regular expressions (REGEXP functions) are available for specific data sources such as Tableau extracts, MySQL, PostgreSQL, Oracle, and others. Consult the Tableau documentation for data source-specific compatibility.
