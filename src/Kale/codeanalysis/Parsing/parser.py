import sys
from codeanalysis.Syntax.tokenkind import TokenKind
# from termcolor import cprint


class Parser:
    def __init__(self, token_list, emitter, debug=False):
        self.token_list = token_list
        self.position = -1
        # self.emitter = emitter
        self.debug = debug

        # Sets the current token to the first token taken from the input
        # ----
        self.symbols = set()
        self.labels_declared = set()
        self.labels_gotoed = set()  # goto'ed
        # ----

        # tokens
        # ----
        self.cur_token = None
        # ----

        self.advance()
        
    def check_token(self, kind):
        """
        Checks whether passed token kind matches the current token kind.
        """

        return kind == self.cur_token.kind

    def peek(self, kind):
        """
        Checks whether passed token kind matches the next token.
        """

        return self.token_list[self.position + 1]

    def match(self, kind):
        """
        Matches the current token kind to the passed token kind.
        
        Exceptions: Raises an error if the token kind doesn't match.
        """

        if not self.check_token(kind):
            self.abort("Expected " + kind.name + ", got " + self.cur_token.kind.name)
        self.advance()
    
    def advance(self, offset=0):
        """
        Sets the current token to the next token.
        """
        self.position += 1 + offset
        if self.position < len(self.token_list):
            self.cur_token = self.token_list[self.position]

    def is_comparison_operator(self):
        """
        Checks whether the current token is a comparison operator.
        """

        return (
                self.check_token(TokenKind.GreaterToken) or self.check_token(TokenKind.GreaterOrEqualsToken) or
                self.check_token(TokenKind.LessToken) or self.check_token(TokenKind.LessOrEqualsToken) or
                self.check_token(TokenKind.EqualsEqualsToken) or self.check_token(TokenKind.BangEqualsToken)
        )

    def abort(self, message):
        """
        Aborts the program with the passed message.
        """

        # cprint("Error: " + message, 'red')
        # sys.exit(0)
        sys.exit("Error: " + message)

    # Production rules.
    def program(self):
        """
        Program entry point
        """
        if self.debug:
            print("Program")

        # self.emitter.add_header("#include <stdio.h>")
        # self.emitter.add_header("int main(void){")

        while not self.check_token(TokenKind.EndOfFileToken):
            self.statement()

        # self.emitter.emit_line("return 0;")
        # self.emitter.emit_line("}")

        for label in self.labels_gotoed:
            if label not in self.labels_declared:
                self.abort("Attempting to goto to undeclared label: " + label)

    def statement(self):
        """
        Statements Parser
        """

        if self.check_token(TokenKind.PrintKeyword):
            """
            Print Statement
            
            Syntax: 
                1.  print(StringKeyword)
                2.  print(EXPRESSION)
            """
            if self.debug:
                print("Print-Statement")

            self.advance()
            self.match(TokenKind.OpenParenthesisToken)

            if self.check_token(TokenKind.StringToken):
                # self.emitter.emit_line("printf(\"{self.cur_token.value}\\n\");")
                self.advance()
            else:
                # self.emitter.emit_line("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                # self.emitter.emit_line("));")
            self.match(TokenKind.CloseParenthesisToken)
        
        elif self.check_token(TokenKind.IfKeyword):
            """
            If/If-else Statement
            
            Syntax: 
                1.  if(EXPRESSION) 
                    { 
                        STATEMENTS 
                    }
                    
                2.  if (COMPARISON) 
                    {
                        STATEMENTS
                    } else {
                        STATEMENTS        
                    }
                3.  if (COMPARISON)
                    {
                        STATEMENTS
                    } else if (COMPARISON)
                    {
                        STATEMENTS
                    } else {
                        STATEMENTS
                    }
            """
            if self.debug:
                print("If-Statement")

            self.advance()

            # First part
            # ----
            self.match(TokenKind.OpenParenthesisToken)
            # self.emitter.emit("if(")

            self.comparison()
            self.match(TokenKind.CloseParenthesisToken)
            # ----
            
            # Second part
            # ----
            self.match(TokenKind.OpenBraceToken)
            # self.emitter.emit_line("){")
            while not self.check_token(TokenKind.CloseBraceToken):
                self.statement()

            self.match(TokenKind.CloseBraceToken)
            # ----

            # optional part
            # ----
            while self.check_token(TokenKind.ElseKeyword):
                """
                1.  else if(CONDITION)
                    {
                        STATEMENTS
                    }
                2.  else
                    {
                        STATEMENTS
                    }
                """
                self.advance()

                if self.check_token(TokenKind.IfKeyword):
                    if self.debug:
                        print("Else-If-Statement")
                    
                    self.advance()

                    # ----
                    self.match(TokenKind.OpenParenthesisToken)
                    self.comparison()
                    self.match(TokenKind.CloseParenthesisToken)
                    # ----
                    self.match(TokenKind.OpenBraceToken)
                    while not self.check_token(TokenKind.CloseBraceToken):
                        self.statement()
                    self.match(TokenKind.CloseBraceToken)

                elif self.check_token(TokenKind.OpenBraceToken):
                    if self.debug:
                        print("Else-Statement")
                    
                    self.advance()
                    
                    # ----
                    while not self.check_token(TokenKind.CloseBraceToken):
                        self.statement()
                    self.match(TokenKind.CloseBraceToken)
                    
                    break

        elif self.check_token(TokenKind.WhileKeyword):
            """
            While Statement

            Syntax:
                1.  while(EXPRESSION)
                    {
                        STATEMENTS
                    }
            """
            if self.debug:
                print("While-Statement")
            
            self.advance()

            # First part
            # ----
            self.match(TokenKind.OpenParenthesisToken)
            # self.emitter.emit("while(")
            self.comparison()
            self.match(TokenKind.CloseParenthesisToken)
            # ----

            # Second part
            # ----
            self.match(TokenKind.OpenBraceToken)
            
            # self.emitter.emit_line("){")
            while not self.check_token(TokenKind.CloseBraceToken):
                self.statement()
            
            self.match(TokenKind.CloseBraceToken)
            # self.emitter.emit_line("}")
            # ----
        
        elif self.check_token(TokenKind.ForKeyword):
            """
            For Statement

            Syntax:
                1.  for(INITIALIZATION; CONDITION; INCREMENT)
                    {
                        STATEMENTS
                    }
            """
            if self.debug:
                print("For-Statement")
            
            self.advance()

            # Initialization, Condition, Increment
            # ----
            self.match(TokenKind.OpenParenthesisToken)
            self.statement()
            self.match(TokenKind.SemiToken)
            self.comparison()
            self.match(TokenKind.SemiToken)
            self.expression()
            self.match(TokenKind.CloseParenthesisToken)
            # ----

            # Body
            # ----
            self.match(TokenKind.OpenBraceToken)
            while not self.check_token(TokenKind.CloseBraceToken):
                self.statement()
            
            self.match(TokenKind.CloseBraceToken)
            # ----

        elif self.check_token(TokenKind.LabelKeyword):
            """
            Label Statement

            Syntax:
                1.  label IDENTIFIER:
            """
            if self.debug:
                print("Label-Statement")

            self.advance()

            # ----
            if self.cur_token.value in self.labels_declared:
                self.abort(f"Label already exists: {self.cur_token.value}")
            self.labels_declared.add(self.cur_token.value)

            # self.emitter.emit_line(self.cur_token.value + ":")

            self.match(TokenKind.IdentifierToken)
            self.match(TokenKind.ColonToken)
            # ----

        elif self.check_token(TokenKind.GotoKeyword):
            """
            Goto Statement

            Syntax:
                1.  goto IDENTIFIER
            """
            if self.debug:
                print("Goto-Statement")
    
            self.advance()
            
            # ----
            self.labels_gotoed.add(self.cur_token.value)
            
            self.match(TokenKind.IdentifierToken)
            # self.emitter.emit_line(f"goto {self.cur_token.value};")
            # ----
        
        elif self.check_token(TokenKind.IntKeyword):
            """
            Integer Declaration

            Syntax:
                1.  int IDENTIFIER = EXPRESSION
            """
            if self.debug:
                print("Int-Statement")
            
            self.advance()

            if self.cur_token.value not in self.symbols:
                self.symbols.add(self.cur_token.value)
            
            # ----
            self.match(TokenKind.IdentifierToken)
            self.match(TokenKind.EqualsToken)
            self.expression()

        elif self.check_token(TokenKind.LetKeyword):
            """
            Let Statement

            Syntax:
                1.  let IDENTIFIER = EXPRESSION
            """
            if self.debug:
                print("Let-Statement")
            
            self.advance()

            # ----
            if self.cur_token.value not in self.symbols:
                self.symbols.add(self.cur_token.value)
                # self.emitter.add_header(f"auto {self.cur_token.value};")
            else:
                self.abort(f"A local variable named '{self.cur_token.value}' is already defined in this scope")

            # self.emitter.emit(self.cur_token.value + " = ")
            self.match(TokenKind.IdentifierToken)
            self.match(TokenKind.EqualsToken)

            if self.check_token(TokenKind.StringToken):
                # self.emitter.emit_line(f"\"{self.cur_token.value}\"")
                self.advance()
                while self.check_token(TokenKind.PlusToken):
                    # self.emitter.emit_line(" + ")

                    self.advance()
                    if self.check_token(TokenKind.StringToken):
                        # self.emitter.emit_line(f"\"{self.cur_token.value}\"")
                        self.advance()
                    elif self.check_token(TokenKind.IdentifierToken):
                        # self.emitter.emit(self.cur_token.value)
                        self.advance()
                    elif self.check_token(TokenKind.NumberToken):
                        # self.emitter.emit(self.cur_token.value)
                        self.advance()
                    else:
                        self.abort("Expected string, number or an identifier")
            else:
                self.expression()
            # self.emitter.emit_line(";")
            # ----
        
        elif self.check_token(TokenKind.VarKeyword):
            """
            Variable Declaration

            Syntax:
                1.  var IDENTIFIER = EXPRESSION
            """
            if self.debug:
                print("Var-Statement")
            
            self.advance()

            # ----
            if self.cur_token.value not in self.symbols:
                self.symbols.add(self.cur_token.value)
                # self.emitter.add_header(f"auto {self.cur_token.value};")

            # self.emitter.emit(f"{self.cur_token.value} = ")
            self.match(TokenKind.IdentifierToken)
            self.match(TokenKind.EqualsToken)

            if self.check_token(TokenKind.StringToken):
                # self.emitter.emit_line(f"\"{self.cur_token.value}\"")
                self.advance()
                while self.check_token(TokenKind.PlusToken):
                    # self.emitter.emit_line(" + ")

                    self.advance()
                    if self.check_token(TokenKind.StringToken):
                        # self.emitter.emit_line(f"\"{self.cur_token.value}\"")
                        self.advance()
                    elif self.check_token(TokenKind.IdentifierToken):
                        # self.emitter.emit(self.cur_token.value)
                        self.advance()
                    elif self.check_token(TokenKind.NumberToken):
                        # self.emitter.emit(self.cur_token.value)
                        self.advance()
                    else:
                        self.abort("Expected string, number or an identifier")
            else:
                self.expression()
            # self.emitter.emit_line(";")
            # ----

        elif self.check_token(TokenKind.InputKeyword):
            """
            Input Statement

            Syntax:
                1.  input IDENTIFIER
            """
            if self.debug:
                print("Input-Statement")
            self.advance()

            # ----
            if self.cur_token.value not in self.symbols:
                self.symbols.add(self.cur_token.value)
                # self.emitter.add_header(f"float {self.cur_token.value};")

            # self.emitter.emit_line("if(0 == scanf(\"%" + "f\", &{self.cur_token.value})) {")
            # self.emitter.emit_line(self.cur_token.value + " = 0;")
            # self.emitter.emit("scanf_s(\"%")
            # self.emitter.emit_line("*s\");")
            # self.emitter.emit_line("}")
            self.match(TokenKind.IdentifierToken)
            # ----

        elif self.check_token(TokenKind.IdentifierToken):
            """
            Assignment Statement

            Syntax:
                1.  IDENTIFIER = EXPRESSION
            """
            if self.debug:
                print("Assignment-Statement")

            self.advance()

            if self.cur_token.value not in self.symbols:
                self.abort(f"The name '{self.cur_token.value}' does not exist in the current convalue")
            
            # self.emitter.emit(self.cur_token.value + " = ")
            self.match(TokenKind.EqualsToken)

            if self.check_token(TokenKind.StringToken):
                # self.emitter.emit_line(f"\"{self.cur_token.value}\"")
                self.advance()
                while self.check_token(TokenKind.PlusToken):
                    # self.emitter.emit_line(" + ")

                    self.advance()
                    if self.check_token(TokenKind.StringToken):
                        # self.emitter.emit_line(f"\"{self.cur_token.value}\"")
                        self.advance()
                    elif self.check_token(TokenKind.IdentifierToken):
                        # self.emitter.emit(self.cur_token.value)
                        self.advance()
                    elif self.check_token(TokenKind.NumberToken):
                        # self.emitter.emit(self.cur_token.value)
                        self.advance()
                    else:
                        self.abort("Expected string, number or an identifier")
            else:
                self.expression()
            # self.emitter.emit_line(";")
        else:
            self.abort(f"Invalid statement at {self.cur_token.kind.name} {self.cur_token.value if self.cur_token.value is not None else ''}")

    def comparison(self):
        """
        Comparison
        
        Syntax:
            1.  EXPRESSION
            2.  EXPRESSION COMPARISON EXPRESSION
            3.  EXPRESSION COMPARISON EXPRESSION...
        """
        if self.debug:
            print("Comparison")
        
        self.expression()
        
        if self.is_comparison_operator():
            # self.emitter.emit(self.cur_token.value)
            self.advance()
            self.expression()

        while self.is_comparison_operator():
            # self.emitter.emit(self.cur_token.value)
            self.advance()
            self.expression()

    def expression(self):
        """
        Expression

        Syntax:
            1.  TERM
            2.  TERM + TERM
            3.  TERM - TERM
        """
        print("Expression")
        self.term()
        while self.check_token(TokenKind.PlusToken) or self.check_token(TokenKind.MinusToken):
            # self.emitter.emit(self.cur_token.value)
            self.advance()
            self.term()

    def term(self):
        """
        Term

        Syntax:
            1.  FACTOR
            2.  FACTOR * FACTOR
            3.  FACTOR / FACTOR
        """
        if self.debug:
            print("Term")
        
        self.unary()

        while self.check_token(TokenKind.StartToken) or self.check_token(TokenKind.SlashToken):
            # self.emitter.emit(self.cur_token.value)
            self.advance()
            self.unary()

    def unary(self):
        """
        Unary

        Syntax:
            1.  PlusToken FACTOR
            2.  MinusToken FACTOR
            3.  NOT FACTOR
            4.  TildeToken FACTOR
            5.  PlusPlusToken FACTOR
            6.  MinusMinusToken FACTOR
            7.  FACTOR
        """
        if (self.check_token(TokenKind.PlusToken) or self.check_token(TokenKind.MinusToken) or
            self.check_token(TokenKind.BangToken) or self.check_token(TokenKind.TildeToken) or
            self.check_token(TokenKind.PlusPlusToken) or self.check_token(TokenKind.MinusMinusToken)):
            print(f"Unary ({self.cur_token.value})")
            # self.emitter.emit(self.cur_token.value)
            self.advance()
        self.primary()
        if (self.check_token(TokenKind.PlusPlusToken) or self.check_token(TokenKind.MinusMinusToken)):
            print(f"Unary ({self.cur_token.value})")
            # self.emitter.emit(self.cur_token.value)
            self.advance()

    def primary(self):
        """
        Primary

        Syntax:
            1.  NUMBER
            2.  StringKeyword
            3.  IDENTIFIER
            4.  (EXPRESSION)
        """
        if self.check_token(TokenKind.NumberToken) or self.check_token(TokenKind.StringToken):
            print(f"Primary ({self.cur_token.value})")
            # self.emitter.emit(self.cur_token.value)
            self.advance()
        elif self.check_token(TokenKind.IdentifierToken):
            if self.cur_token.value not in self.symbols:
                self.abort(f"Referencing variable before assignment: {self.cur_token.value}")
            
            print(f"Primary ({self.cur_token.value})")
            # self.emitter.emit(self.cur_token.value)
            self.advance()
        elif self.check_token(TokenKind.LPAREN):
            print("Primary (")
            self.advance()
            self.expression()
            self.match(TokenKind.RPAREN)
            print(")")
        else:
            self.abort(f"Unexpected token at {self.cur_token.value}")
