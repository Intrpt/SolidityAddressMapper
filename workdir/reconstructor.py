class SolidityASTReconstructor:
    def __init__(self):
        # Map nodeTypes to handler methods
        self._handlers = {
            'ArrayTypeName': self._handle_array_type,
            'Assignment': self._handle_assignment,
            'BinaryOperation': self._handle_binary_operation,
            'Block': self._handle_block,
            'Break': self._handle_break,
            'Conditional': self._handle_conditional,
            'Continue': self._handle_continue,
            'ContractDefinition': self._handle_contract_definition,
            'DoWhileStatement': self._handle_do_while_statement,
            'ElementaryTypeName': self._handle_elementary_type_name,
            'ElementaryTypeNameExpression': self._handle_elementary_type_name_expression,
            'EmitStatement': self._handle_emit,
            'EnumDefinition': self._handle_enum_definition,
            'EnumValue': self._handle_enum_value,
            'ErrorDefinition': self._handle_error_definition,
            'EventDefinition': self._handle_event_definition,
            'ExpressionStatement': self._handle_expression_statement,
            'ForStatement': self._handle_for,
            'FunctionCall': self._handle_function_call,
            'FunctionCallOptions': self._handle_function_call_options,
            'FunctionDefinition': self._handle_function_definition,
            'FunctionTypeName': self._handle_function_type_name,
            'Identifier': self._handle_identifier,
            'IdentifierPath': self._handle_identifier_path,
            'IfStatement': self._handle_if,
            'ImportDirective': self._handle_import_directive,
            'IndexAccess': self._handle_index_access,
            'IndexRangeAccess': self._handle_index_range_access,
            'InheritanceSpecifier': self._handle_inheritance_specifier,
            'InlineAssembly': self._handle_inline_assembly,
            'Literal': self._handle_literal,
            'Mapping': self._handle_mapping,
            'MemberAccess': self._handle_member_access,
            'ModifierDefinition': self._handle_modifier_definition,
            'ModifierInvocation': self._handle_modifier_invocation,
            'NewExpression': self._handle_new_expression,
            'OverrideSpecifier': self._handle_override_specifier,
            'ParameterList': self._handle_parameter_list,
            'PlaceHolderStatement': self._handle_placeholder,
            'PragmaDirective': self._handle_pragma_directive,
            'Return': self._handle_return,
            'RevertStatement': self._handle_revert,
            'SourceUnit': self._handle_source_unit,
            'StorageLayoutSpecifier': self._handle_storage_layout_specifier,
            'StructDefinition': self._handle_struct_definition,
            'StructuredDocumentation': self._handle_structured_documentation,
            'TryCatchClause': self._handle_try_catch,
            'TryStatement': self._handle_try,
            'TupleExpression': self._handle_tuple_expression,
            'TypeDescriptions': self._handle_type_descriptions,
            'UnaryOperation': self._handle_unary_operation,
            'UncheckedBlock': self._handle_unchecked_block,
            'UserDefinedTypeName': self._handle_user_defined_type_name,
            'UserDefinedValueTypeDefinition': self._handle_user_defined_value_type_definition,
            'UsingForDirective': self._handle_using_for_directive,
            'VariableDeclaration': self._handle_variable_declaration,
            'VariableDeclarationStatement': self._handle_var_decl_stmt,
            'WhileStatement': self._handle_while,
            'YulAssignment': self._handle_yul_assignment,
            'YulBlock': self._handle_yul_block,
            'YulBreak': self._handle_yul_break,
            'YulLeave': self._handle_yul_leave,
            'YulLiteralHexValue': self._handle_yul_literal_hex_value,
            'YulLiteralValue': self._handle_yul_literal_value,
            'YulSwitch': self._handle_yul_switch,
            'YulTypedName': self._handle_yul_typed_name,
            'YulVariableDeclaration': self._handle_yul_variable_declaration

        }


    def reconstruct(self, node: dict) -> str:
        if not isinstance(node, dict):
            return ''
        node_type = node.get('nodeType')
        if not node_type:
            return ''
        handler = self._handlers.get(node_type)
        if handler:
            return handler(node)
        return f"<unhandled {node_type}>"


    def _handle_break(self, node, **kwargs):
        """Handle Break statement node."""
        return "break"


    def _handle_continue(self, node, **kwargs):
        """Handle Continue statement node."""
        return "continue"


    def _handle_elementary_type_name(self, node, **kwargs):
        """Handle ElementaryTypeName node."""
        return node.get('name', '')


    def _handle_function_type_name(self, node, **kwargs):
        """Handle FunctionTypeName node."""
        params = self.reconstruct(node.get('parameterTypes', {}))
        return_params = self.reconstruct(node.get('returnParameterTypes', {}))
        visibility = node.get('visibility', 'internal')
        stateMutability = node.get('stateMutability', '')

        result = f"function({params})"
        if return_params:
            result += f" returns ({return_params})"
        if visibility != 'internal':
            result += f" {visibility}"
        if stateMutability:
            result += f" {stateMutability}"

        return result


    def _handle_identifier_path(self, node, **kwargs):
        """Handle IdentifierPath node."""
        return node.get('name', '')


    def _handle_import_directive(self, node, **kwargs):
        """Handle ImportDirective node."""
        path = node.get('absolutePath', '')

        if node.get('unitAlias', ''):
            return f'import "{path}" as {node["unitAlias"]};'
        elif node.get('symbolAliases', []):
            symbols = []
            for alias in node['symbolAliases']:
                if isinstance(alias, dict) and 'foreign' in alias and 'local' in alias:
                    name = self.reconstruct(alias['foreign'])
                    alias_name = alias.get('local', name)
                    if alias_name and alias_name != name:
                        symbols.append(f"{name} as {alias_name}")
                    else:
                        symbols.append(name)
                elif isinstance(alias, list) and len(alias) == 2:
                    name = self.reconstruct(alias[0])
                    alias_name = alias[1]
                    if alias_name and alias_name != name:
                        symbols.append(f"{name} as {alias_name}")
                    else:
                        symbols.append(name)
            return f'import {{{", ".join(symbols)}}} from "{path}";'
        else:
            return f'import "{path}";'


    def _handle_index_range_access(self, node, **kwargs):
        """Handle IndexRangeAccess node."""
        base = self.reconstruct(node.get('baseExpression', {}))
        start_index = self.reconstruct(node.get('startIndex', {}))
        end_index = self.reconstruct(node.get('endIndex', {}))

        if end_index:
            return f"{base}[{start_index}:{end_index}]"
        return f"{base}[{start_index}:]"


    def _handle_inheritance_specifier(self, node, **kwargs):
        """Handle InheritanceSpecifier node."""
        base_name = self.reconstruct(node.get('baseName', {}))
        args = self.reconstruct(node.get('arguments', {}))

        if args:
            return f"{base_name}({args})"
        return base_name


    def _handle_inline_assembly(self, node, **kwargs):
        """Handle InlineAssembly node."""
        yul_block = self.reconstruct(node.get('yulBlock', {})) or self.reconstruct(node.get('operations', {}))
        language = node.get('language', '')

        if language:
            return f"assembly {language} {{{yul_block}}}"
        return f"assembly {{{yul_block}}}"


    def _handle_mapping(self, node, **kwargs):
        """Handle Mapping node."""
        key_type = self.reconstruct(node.get('keyType', {}))
        value_type = self.reconstruct(node.get('valueType', {}))

        return f"mapping({key_type} => {value_type})"


    def _handle_modifier_invocation(self, node, **kwargs):
        """Handle ModifierInvocation node."""
        name = self.reconstruct(node.get('modifierName', {}))
        args = self.reconstruct(node.get('arguments', {}))

        if args:
            return f"{name}({args})"
        return name


    def _handle_override_specifier(self, node, **kwargs):
        """Handle OverrideSpecifier node."""
        overrides = node.get('overrides', [])

        if overrides:
            override_names = [self.reconstruct(o) for o in overrides]
            return f"override({', '.join(override_names)})"
        return "override"


    def _handle_parameter_list(self, node, **kwargs):
        """Handle ParameterList node."""
        parameters = node.get('parameters', [])
        param_strs = [self.reconstruct(param) for param in parameters]

        return ', '.join(param_strs)


    def _handle_placeholder(self, node, **kwargs):
        """Handle PlaceHolderStatement node."""
        return "_"


    def _handle_source_unit(self, node, **kwargs):
        """Handle SourceUnit node."""
        nodes = node.get('nodes', [])
        source_unit_parts = [self.reconstruct(n) for n in nodes]

        return '\n'.join(source_unit_parts)


    def _handle_storage_layout_specifier(self, node, **kwargs):
        """Handle StorageLayoutSpecifier node."""
        storage_type = node.get('storage')
        return f"storage {storage_type}"


    def _handle_structured_documentation(self, node, **kwargs):
        """Handle StructuredDocumentation node."""
        text = node.get('text', '')
        return f"/**\n * {text}\n */"


    def _handle_try_catch(self, node, **kwargs):
        """Handle TryCatchClause node."""
        parameters = self.reconstruct(node.get('parameters', {}))
        body = self.reconstruct(node.get('block', {}))
        error_name = node.get('errorName', '')

        if error_name:
            return f"catch {error_name}({parameters}) {body}"
        return f"catch({parameters}) {body}"


    def _handle_try(self, node, **kwargs):
        """Handle TryStatement node."""
        expr = self.reconstruct(node.get('externalCall', {}))
        try_block = self.reconstruct(node.get('clauses', [{}])[0].get('block', {}))
        catch_clauses = [self.reconstruct(c) for c in node.get('clauses', [])[1:]]

        result = f"try {expr} {try_block}"
        for catch_clause in catch_clauses:
            result += f" {catch_clause}"

        return result


    def _handle_type_descriptions(self, node, **kwargs):
        """Handle TypeDescriptions node."""
        type_string = node.get('typeString', '')
        return type_string


    def _handle_unchecked_block(self, node, **kwargs):
        """Handle UncheckedBlock node."""
        statements = node.get('statements', [])
        body = '\n'.join(self.reconstruct(stmt) for stmt in statements)

        return f"unchecked {{\n{body}\n}}"


    def _handle_user_defined_type_name(self, node, **kwargs):
        """Handle UserDefinedTypeName node."""
        path_nodes = node.get('pathNode', {})
        if path_nodes:
            return self.reconstruct(path_nodes)
        return node.get('name', '')


    def _handle_user_defined_value_type_definition(self, node, **kwargs):
        """Handle UserDefinedValueTypeDefinition node."""
        name = node.get('name', '')
        underlying_type = self.reconstruct(node.get('underlyingType', {}))

        return f"type {name} is {underlying_type};"


    def _handle_variable_declaration(self, node, **kwargs):
        """Handle VariableDeclaration node."""
        typ = self.reconstruct(node.get('typeName', {}))
        name = node.get('name', '')
        visibility = node.get('visibility', '')
        state_mutability = node.get('stateMutability', '')
        storage_location = node.get('storageLocation', '')
        value = node.get('value', {})

        result = []
        if typ:
            result.append(typ)

        if storage_location:
            result.append(storage_location)

        if name:
            result.append(name)

        if visibility:
            result.append(visibility)

        if state_mutability:
            result.append(state_mutability)

        if value:
            result.append(f"= {self.reconstruct(value)}")

        return ' '.join(result)


    def _handle_yul_assignment(self, node, **kwargs):
        """Handle YulAssignment node."""
        variable_names = node.get('variableNames', [])
        value = self.reconstruct(node.get('value', {}))

        var_names = [self.reconstruct(var) for var in variable_names]
        return f"{', '.join(var_names)} := {value}"


    def _handle_yul_block(self, node, **kwargs):
        """Handle YulBlock node."""
        statements = node.get('statements', [])
        body = '\n'.join(self.reconstruct(stmt) for stmt in statements)

        return body


    def _handle_yul_break(self, node, **kwargs):
        """Handle YulBreak node."""
        return "break"


    def _handle_yul_leave(self, node, **kwargs):
        """Handle YulLeave node."""
        return "leave"


    def _handle_yul_literal_hex_value(self, node, **kwargs):
        """Handle YulLiteralHexValue node."""
        value = node.get('value', '')
        kind = node.get('kind', '')

        if kind == 'number':
            return f"0x{value}"
        return f'hex"{value}"'


    def _handle_yul_literal_value(self, node, **kwargs):
        """Handle YulLiteralValue node."""
        value = node.get('value', '')
        kind = node.get('kind', '')

        if kind == 'string':
            return f'"{value}"'
        return value


    def _handle_yul_switch(self, node, **kwargs):
        """Handle YulSwitch node."""
        expression = self.reconstruct(node.get('expression', {}))
        cases = node.get('cases', [])

        case_blocks = []
        for case in cases:
            if case.get('default', False):
                body = self.reconstruct(case.get('body', {}))
                case_blocks.append(f"default {{ {body} }}")
            else:
                value = self.reconstruct(case.get('value', {}))
                body = self.reconstruct(case.get('body', {}))
                case_blocks.append(f"case {value} {{ {body} }}")

        return f"switch {expression} {' '.join(case_blocks)}"


    def _handle_yul_typed_name(self, node, **kwargs):
        """Handle YulTypedName node."""
        return node.get('name', '')


    def _handle_yul_variable_declaration(self, node, **kwargs):
        """Handle YulVariableDeclaration node."""
        variables = node.get('variables', [])
        value = node.get('value', {})

        var_names = [self.reconstruct(var) for var in variables]

        if value:
            return f"let {', '.join(var_names)} := {self.reconstruct(value)}"
        return f"let {', '.join(var_names)}"


    def _handle_error_definition(self, node):
        name = node.get('name', '')
        parameters = self.reconstruct(node.get('parameters', {}))
        return f"error {name}({parameters});"

    def _handle_elementary_type_name_expression(self, node):
        """
        Handles type conversions like uint(42) or address(someVar).
        """
        type_name = self.reconstruct(node.get('typeName', {}))
        argument = self.reconstruct(node.get('argument', {}))
        return f"{type_name}({argument})"

    def _handle_array_type(self, node):
        base_type = self.reconstruct(node.get('baseType', {}))
        length_expr = node.get('length')
        if length_expr:
            length = self.reconstruct(length_expr)
            return f"{base_type}[{length}]"
        return f"{base_type}[]"

    def _handle_do_while_statement(self, node):
        cond = self.reconstruct(node.get('condition', {}))
        body = self.reconstruct(node.get('body', {}))
        return f"do {body} while ({cond});"


    # === Expression Handlers ===
    def _handle_literal(self, node):
        kind = node.get('kind')
        value = node.get('value', '')
        if kind == 'string':
            return f'"{value}"'
        if kind == 'bool':
            return 'true' if value else 'false'
        return str(value)

    def _handle_identifier(self, node):
        return node.get('name', '')

    def _handle_binary_operation(self, node):
        left = self.reconstruct(node.get('leftExpression', {}))
        right = self.reconstruct(node.get('rightExpression', {}))
        op = node.get('operator', '')
        return f"({left} {op} {right})"

    def _handle_unary_operation(self, node):
        expr = self.reconstruct(node.get('subExpression', {}))
        op = node.get('operator', '')
        return f"{op}{expr}" if node.get('prefix', True) else f"{expr}{op}"

    def _handle_assignment(self, node):
        left = self.reconstruct(node.get('leftHandSide', {}))
        right = self.reconstruct(node.get('rightHandSide', {}))
        op = node.get('operator', '=')
        return f"{left} {op} {right}"

    def _handle_function_call(self, node):
        expr = self.reconstruct(node.get('expression', {}))
        args = [self.reconstruct(arg) for arg in node.get('arguments', [])]
        return f"{expr}({', '.join(args)})"

    def _handle_function_call_options(self, node):
        expr = self.reconstruct(node.get('expression', {}))
        names = node.get('names', [])
        opts = [f"{name}: {self.reconstruct(opt)}" for name, opt in zip(names, node.get('options', []))]
        args = node.get('arguments') or node.get('expression', {}).get('arguments', [])
        args_str = ', '.join(self.reconstruct(arg) for arg in args)
        return f"{expr}{{{', '.join(opts)}}}({args_str})"

    def _handle_member_access(self, node):
        expr = self.reconstruct(node.get('expression', {}))
        return f"{expr}.{node.get('memberName', '')}"

    def _handle_index_access(self, node):
        base = self.reconstruct(node.get('baseExpression', {}))
        index = self.reconstruct(node.get('indexExpression', {}))
        return f"{base}[{index}]"

    def _handle_tuple_expression(self, node):
        components = [self.reconstruct(c) for c in node.get('components', [])]
        return f"({', '.join(components)})"

    def _handle_new_expression(self, node):
        return f"new {self.reconstruct(node.get('typeName', {}))}"

    def _handle_conditional(self, node):
        cond = self.reconstruct(node.get('condition'))
        true_expr = self.reconstruct(node.get('trueExpression'))
        false_expr = self.reconstruct(node.get('falseExpression'))
        return f"{cond} ? {true_expr} : {false_expr}"

    # === Statement Handlers ===
    def _handle_expression_statement(self, node):
        return self.reconstruct(node.get('expression', {})) + ';'

    def _handle_return(self, node):
        expr = self.reconstruct(node.get('expression')) if node.get('expression') else ''
        return f"return {expr};" if expr else "return;"

    def _handle_if(self, node):
        cond = self.reconstruct(node.get('condition'))
        true_body = self.reconstruct(node.get('trueBody'))
        false_body = self.reconstruct(node.get('falseBody')) if node.get('falseBody') else ''
        return f"if ({cond}) {true_body}" + (f" else {false_body}" if false_body else "")

    def _handle_while(self, node):
        cond = self.reconstruct(node.get('condition'))
        body = self.reconstruct(node.get('body'))
        return f"while ({cond}) {body}"

    def _handle_for(self, node):
        init = self.reconstruct(node.get('initializationExpression', {}))
        cond = self.reconstruct(node.get('condition', {}))
        loop = self.reconstruct(node.get('loopExpression', {}))
        body = self.reconstruct(node.get('body', {}))
        return f"for ({init} {cond}; {loop}) {body}"

    def _handle_var_decl_stmt(self, node):
        decls = [self.reconstruct(d) for d in node.get('declarations', [])]
        if node.get('initialValue'):
            init = self.reconstruct(node['initialValue'])
            return f"{', '.join(decls)} = {init};"
        return f"{', '.join(decls)};"

    def _handle_emit(self, node):
        event_call = self.reconstruct(node.get('eventCall', {}))
        return f"emit {event_call};"

    def _handle_revert(self, node):
        expr = self.reconstruct(node.get('expression')) if node.get('expression') else ''
        return f"revert({expr});" if expr else "revert();"

    def _handle_block(self, node):
        statements = [self.reconstruct(s) for s in node.get('statements', [])]
        return "{\n" + "\n".join(statements) + "\n}"

    # === Declaration Handlers ===
    def _handle_function_definition(self, node):
        name = node.get('name', '')
        params = node.get('parameters', {}).get('parameters', [])
        ret_params = node.get('returnParameters', {}).get('parameters', [])
        visibility = node.get('visibility', '')
        mutability = node.get('stateMutability', '')
        param_str = ', '.join(self.reconstruct(p) for p in params)
        ret_str = ''
        if ret_params:
            ret_str = ' returns (' + ', '.join(self.reconstruct(p) for p in ret_params) + ')'
        body = self.reconstruct(node.get('body')) if node.get('body') else ';'
        return f"function {name}({param_str}) {visibility} {mutability}{ret_str} {body}"

    def _handle_enum_value(self, node):
        name = node.get("name", "<unnamed>")
        return f"Enum value {name}"

    def _handle_contract_definition(self, node):
        name = node.get("name", "<unnamed>")
        return f"Contract {name}"

    def _handle_enum_definition(self, node):
        name = node.get("name", "<unnamed>")
        return f"Enum {name}"

    def _handle_event_definition(self, node):
        name = node.get("name", "<unnamed>")
        return f"Event {name}"

    def _handle_modifier_definition(self, node):
        name = node.get("name", "<unnamed>")
        return f"Modifier {name}"

    def _handle_pragma_directive(self, node):
        literals = " ".join(node.get("literals", []))
        return f"Pragma {literals}"

    def _handle_state_variable_declaration(self, node):
        variables = [v["name"] for v in node.get("variables", [])]
        return f"State Variables: {', '.join(variables)}"

    def _handle_struct_definition(self, node):
        name = node.get("name", "<unnamed>")
        return f"Struct {name}"

    def _handle_using_for_directive(self, node):
        library_name = node.get("libraryName", "<unknown>")
        type_name = node.get("typeName", "<all>")
        return f"Using {library_name} for {type_name}"
