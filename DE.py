from sympy import symbols, Function, simplify, S, cos, collect, expand
import sympy as sp

def is_homogeneous(expr, vars):
    """
    Check if the given function is homogeneous and determine its degree.

    Parameters:
        expr: sympy expression
            The function to check.
        vars: list of sympy symbols
            The variables in the function.

    Returns:
        (bool, float):
            A tuple where the first element indicates if the function is homogeneous,
            and the second element is the degree of homogeneity (if applicable).
    """
    t = symbols('t')  # Scaling factor
    scaled_vars = [t * var for var in vars]
    scaled_expr = expr.subs(dict(zip(vars, scaled_vars))).expand()

    degree = None
    for term in scaled_expr.as_ordered_terms():
        ratio = simplify(term / expr)
        if ratio.has(t):
 
            t_degree = collect(ratio, t).as_coeff_exponent(t)[1]
            if degree is None:
                degree = t_degree
            elif degree != t_degree:
                return False, None  
    return True, degree if degree is not None else 0


x, y = symbols('x y')
expr1 = y**x

print(is_homogeneous(expr1, [x, y]))  
