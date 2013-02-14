

class Expr(object):

    (
        TYPE_ALL,
        TYPE_OR,
        TYPE_AND,
        TYPE_NOT,
        TYPE_EQUALS,
        TYPE_IN,
        TYPE_NAME,
        TYPE_CATEGORY
    ) = range(8)

    def evaluate(self):
        pass

    def __bool__(self):
        return self.evaluate()


class Eq(Expr):

    type = Expr.TYPE_EQUALS

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def evaluate(self):
        return (self.lhs == self.rhs)

    def __str__(self):
        return "(%s) == (%s)" % (self.lhs, self.rhs)


class In(Expr):

    type = Expr.TYPE_IN

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def evaluate(self):
        return bool(self.lhs in self.rhs)

    def __str__(self):
        return "(%s) in (%s)" % (self.lhs, self.rhs)


class All(object):
    
    type = Expr.TYPE_ALL

    def evaluate(self):
        return True

    def __str__(self):
        return "True"


class And(Expr):

    type = Expr.TYPE_AND

    def __init__(self, *args):
        self.exprs = list(args)

    def evaluate(self):
        prev = self.exprs[0].evaluate()
        for next in self.exprs[1:]:
            prev = bool(prev and next.evaluate())
        return prev

    def __str__(self):
        return " and ".join(["(%s)" % expr for expr in self.exprs])


class Or(Expr):

    type = Expr.TYPE_OR

    def __init__(self, *args):
        self.exprs = list(args)

    def evaluate(self):
        prev = self.exprs[0].evaluate()
        for next in self.exprs[1:]:
            prev = bool(prev or next.evaluate())
        return prev

    def __str__(self):
        return " or ".join(["(%s)" % expr for expr in self.exprs])


class Not(Expr):

    type = Expr.TYPE_NOT

    def __init__(self, expr):
        self.expr = expr

    def evaluate(self):
        return not self.expr.evaluate()

    def __str__(self):
        return "not (%s)" % self.expr


class Name(Eq):

    type = Expr.TYPE_NAME

    def __init__(self, value, context=None):
        super(Name, self).__init__(
            context,
            value.strip().replace("\\", r"\\").replace("'", r"\'")
        )

    def __str__(self):
        return "('%s') == ('%s')" % (self.lhs, self.rhs)


class Category(In):

    type = Expr.TYPE_CATEGORY

    def __init__(self, value, context=None):
        super(Category, self).__init__(value.strip(), context)

    def __str__(self):
        return "('%s') in (%s)" % (self.lhs, self.rhs)


if __name__ == "__main__":

    import xml.etree.cElementTree as etree

    class MockMenuEntry(object):

        def __init__(self, id, categories):
            self.DesktopFileID = id
            self.Categories = categories

        def __str__(self):
            return "<%s: %s>" % (self.DesktopFileID, self.Categories)

    def parse_rule(node, parent_expr=None):
        if parent_expr is None:
            expr = Or()
            for child in node:
                expr.exprs.append(parse_node(child, expr))
        else:
            expr = parse_node(node, parent_expr)
        return expr

    def parse_node(node, expr):
        t = node.tag
        if t == 'Or':
            return parse_or(node, expr)
        elif t == 'And':
            return parse_and(node, expr)
        elif t == 'Not':
            return parse_not(node, expr)
        elif t == 'Category':
            return parse_category(node, expr)
        elif t == 'Name':
            return parse_name(node, expr)

    def parse_and(node, expr):
        child_expr = And()
        for child in node:
            rule = parse_node(child, child_expr)
            child_expr.exprs.append(rule)
        return child_expr
        #expr.exprs.append(child_expr)

    def parse_or(node, expr):
        child_expr = Or()
        for child in node:
            rule = parse_node(child, child_expr)
            child_expr.exprs.append(rule)
        return child_expr
        #expr.exprs.append(child_expr)

    def parse_not(node, expr):
        child_expr = Or()
        for child in node:
            rule = parse_node(child, child_expr)
            child_expr.exprs.append(rule)
        return Not(child_expr)

    def parse_category(node, expr):
        return Category(node.text)

    def parse_name(node, expr):
        return Name(node.text)

    def walker(expr, context, depth=0):
        #print ('--' * depth) + repr(expr)
        t = expr.type
        if t == Expr.TYPE_CATEGORY:
            expr.rhs = context.Categories
        if t == Expr.TYPE_NAME:
            expr.lhs = context.DesktopFileID
        if t == Expr.TYPE_OR or t == Expr.TYPE_AND:
            for child in expr.exprs:
                walker(child, context, depth+1)
        else:
            walker(expr.expr, context, depth+1)

    def evaluate(rule, menuentry):
        walker(rule, menuentry)
        return rule.evaluate()

    xml = """
    <Include>
        <And>
            <Category>Accessibility</Category>
            <Not>
                <Category>Settings</Category>
            </Not>
        </And>
        <Name>screenreader.desktop</Name>
    </Include>
    """
    root = etree.fromstring(xml)

    rule = parse_rule(root)

    entries = (
        ('app1.desk', ['Accessibility'], True),
        ('app2.desk', ['Accessibility', 'Settings'], False),
        ('app3.desk', ['Accessibility', 'Preferences'], True),
        ('app4.desk', ['Graphics', 'Settings'], False),
        ('screenreader.desktop', ['Utility', 'Other'], True)
    )
    for i, entry in enumerate(entries):
        menuentry = MockMenuEntry(entry[0], entry[1])
        result = evaluate(rule, menuentry)
        assert result == entry[2], "Error with result set %s: got %s, expected %s" % (
            i, result, entry[2]
        )
