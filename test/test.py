from dataclasses import dataclass
import unittest
from null_safety import Null, nullable
from null_safety.null_safety import undo_nullable

class NullTestSuite(unittest.TestCase):
    def test_null_is_singleton(self):
        self.assertIs(Null, Null)
    
    def test_null_ifn_returns_null(self):
        self.assertIs(Null.ifn.__str__, Null)
    
    def test_nullable_of_null_is_null(self):
        self.assertIs(nullable(Null), Null)
    
    def test_nullable_of_none_is_null(self):
        self.assertIs(nullable(None), Null)
    
    def test_null_is_falsy(self):
        self.assertFalse(bool(Null))
    
    def test_attribute_error_of_null_is_of_null(self):
        with self.assertRaises(AttributeError):
            try:
                Null.asdf
            except AttributeError as e:
                self.assertIs(e.obj, Null)
                raise e
        
            

class nullableTestSuite(unittest.TestCase):
    def test_nullable_of_object_is_object(self):
        @dataclass
        class Guerrero:
            vida: int
            ataque: int
        atila = Guerrero(100, 100)
        self.assertIs(nullable(atila), atila)
    
    def test_nullable_object_understands_ifn(self):
        @dataclass
        class Guerrero:
            vida: int
            ataque: int
        self.assertTrue(hasattr(nullable(Guerrero(100, 100)), 'ifn'))
        
    def test_ifn_in_nullable_object_gets_attribute(self):
        @dataclass
        class Guerrero:
            vida: int
            ataque: int
        self.assertIs(nullable(Guerrero(100, 100)).ifn.vida, 100)
    
    def test_nullable_is_applicable_to_class(self):
        @nullable
        class Guerrero:
            def __init__(self, vida, ataque):
                self.vida = vida
                self.ataque = ataque
        
        self.assertIs(Guerrero(100, 100).ifn.vida, 100)

    def test_inmutable_object_can_be_nullable(self):
        self.assertTrue(hasattr(nullable(object()), 'ifn'))
    
    def test_inmutable_object_keep_their_special_methods(self):
        self.assertTrue(hasattr(nullable([]), '__str__'))
        self.assertEqual(str(nullable([])), '[]')
    
    def test_inmutable_object_return_nullable_objects(self):
        popped = nullable([1, 2, 3]).pop()
        self.assertTrue(hasattr(popped, 'ifn'))
        self.assertEqual(popped, 3)
    
    def test_inmutable_class_can_be_made_nullable(self):
        self.assertTrue(hasattr(nullable(int), 'ifn'))
    
    def test_instance_of_inmutable_class_is_nullable(self):
        nullable_int = nullable(int)
        self.assertTrue(hasattr(nullable_int(3), 'ifn'))
        self.assertEqual(nullable_int(3), 3)
    
    def test_user_defined_special_method_in_object(self):
        class Guerrero:
            __slots__ = ('vida',)
            def __init__(self, vida):
                self.vida = vida
            
            def __str__(self):
                return f"#Guerrero({self.vida})"
        self.assertEqual(str(nullable(Guerrero(100))), "#Guerrero(100)")
    
    def test_user_defined_special_method(self):
        @nullable
        class Guerrero:
            __slots__ = ('vida',)
            def __init__(self, vida):
                self.vida = vida
            
            def __str__(self):
                return f"#Guerrero({self.vida})"
        self.assertEqual(str(Guerrero(100)), "#Guerrero(100)")

class UndoNullableTestSuite(unittest.TestCase):
    def test_undo_none_is_none(self):
        self.assertIs(undo_nullable(None), None)
    
    def test_undo_null_is_none(self):
        self.assertIs(undo_nullable(Null), None)
    
    def test_undo_of_object_is_object(self):
        class Guerrero:
            vida: int
            ataque: int
        atila = Guerrero()
        nullable_atila = nullable(atila)
        undone_atile = undo_nullable(nullable_atila)
        self.assertIs(undone_atile, atila)
        # TODO: decidir que quiero hacer con el atributo ifn
        #self.assertFalse(hasattr(undone_atile, 'ifn'))
    
    def test_undo_of_inmutable_object_is_object(self):
        atila = object()
        nullable_atila = nullable(atila)
        undone_atile = undo_nullable(nullable_atila)
        self.assertIs(undone_atile, atila)
        # TODO: decidir que quiero hacer con el atributo ifn
        #self.assertFalse(hasattr(undone_atile, 'ifn'))
    
    def test_undo_of_class_is_class(self):
        class Guerrero:
            vida: int
            ataque: int
        nullable_guerrero = nullable(Guerrero)
        self.assertIs(undo_nullable(nullable_guerrero), Guerrero)
    
    def test_undo_of_inmutable_class_is_class(self):
        nullable_str = nullable(str)
        self.assertIs(undo_nullable(nullable_str), str)

class SetterTestSuite(unittest.TestCase):
    def test_set_attribute_in_class(self):
        class Guerrero:
            ...
        NullableGuerrero = nullable(Guerrero)
        NullableGuerrero.atacar = lambda *args: ...
        self.assertTrue(hasattr(Guerrero, 'atacar'))
    
    def test_set_attribute_in_object(self):
        class Guerrero:
            def __init__(self, vida):
                self.vida = vida
        atila = Guerrero(100)
        nullable_atila = nullable(atila)
        nullable_atila.vida = 10
        self.assertEqual(atila.vida, 10)
    
    def test_set_attribute_in_inmutable_object(self):
        nullable_three = nullable(3)
        with self.assertRaises(AttributeError):
            try:
                nullable_three.asdf = None
            except AttributeError as e:
                self.assertIn("'int'", e.args[0])
                raise e
    
    def test_set_attribute_in_inmutable_class(self):
        nullable_int = nullable(int)
        with self.assertRaises(TypeError):
            try:
                nullable_int.asdf = None
            except TypeError as e:
                self.assertIn('asdf', e.args[0])
                raise e
