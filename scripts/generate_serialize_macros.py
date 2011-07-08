#!/usr/bin/env python
import sys

"""This script is used to generate the RDB_MAKE_SERIALIZABLE_*() and
RDB_MAKE_ME_SERIALIZABLE_*() macro definitions. Because there are so
many variations, and because they are so similar, it's easier to just
have a Python script to generate them.

This script is meant to be run as follows (assuming you are in the
"rethinkdb/src" directory):

$ ../scripts/generate_serialize_macros.py > rpc/serialize/serialize_macros.hpp

"""


def generate_make_serializable_macro(nfields):
    print "#define RDB_MAKE_SERIALIZABLE_%d(type_t%s) \\" % \
        (nfields, "".join(", field%d" % (i+1) for i in xrange(nfields)))
    print "    namespace boost {\\"
    print "    namespace serialization {\\"
    print "    template<class Archive> void serialize(%sArchive &ar, type_t &m, UNUSED const unsigned int version) { \\"  % ("UNUSED " if nfields == 0 else "")
    for i in xrange(nfields):
        print "        ar & m.field%d; \\" % (i+1)
    print "    }}} \\"
    # See the note in the comment below.
    print "    extern int dont_use_RDB_MAKE_SERIALIZABLE_within_a_class_body;"

def generate_make_me_serializable_macro(nfields):
    print "#define RDB_MAKE_ME_SERIALIZABLE_%d(%s) \\" % \
        (nfields, ", ".join("field%d" % (i+1) for i in xrange(nfields)))
    print "    friend class boost::serialization::access; \\"
    print "    template<typename Archive> void serialize(%sArchive &ar, UNUSED const unsigned int version) { \\"  % ("UNUSED " if nfields == 0 else "")
    for i in xrange(nfields):
        print "        ar & field%d; \\" % (i+1)
    print "    } \\"

if __name__ == "__main__":

    print "#ifndef __RPC_SERIALIZE_SERIALIZE_MACROS_HPP__"
    print "#define __RPC_SERIALIZE_SERIALIZE_MACROS_HPP__"
    print

    print "/* This file is automatically generated by '%s'." % " ".join(sys.argv)
    print "Please modify '%s' instead of modifying this file.*/" % sys.argv[0]
    print

    print "#include <boost/serialize/serialize.hpp>"
    print "#include \"rpc/serialize/serialize.hpp\""
    print

    print """
/* The purpose of these macros is to make it easier to serialize and
unserialize data types that consist of a simple series of fields, each of which
is serializable. Suppose we have a type "struct point_t { int x, y; }" that we
want to be able to serialize. To make it serializable automatically, either
write RDB_MAKE_SERIALIZABLE_2(point_t, x, y) at the global scope or write
RDB_MAKE_ME_SERIALIZABLE(x, y) within the body of the point_t type.
The reason for the second form is to make it possible to serialize template
types. There is at present no non-intrusive way to use these macros to
serialize template types; this is less-than-ideal, but not worth fixing right
now.

A note about "dont_use_RDB_MAKE_SERIALIZABLE_within_a_class_body": It's wrong
to invoke RDB_MAKE_SERIALIZABLE_*() within the body of a class. You should
invoke it at global scope after the class declaration, or use
RDB_MAKE_ME_SERIALIZABLE_*() instead. In order to force the compiler to catch
this error, we declare a dummy "extern int" in RDB_MAKE_ME_SERIALIZABLE_*().
This is a noop at the global scope, but produces a (somewhat weird) error in
the class scope. */
    """.strip()
    print

    for nfields in xrange(20):
        generate_make_serializable_macro(nfields)
        generate_make_me_serializable_macro(nfields)
        print

    print "#endif /* __RPC_SERIALIZE_SERIALIZE_MACROS_HPP__ */"
