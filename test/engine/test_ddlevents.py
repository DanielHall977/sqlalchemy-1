from unittest import mock
from unittest.mock import Mock

import sqlalchemy as tsa
from sqlalchemy import create_engine
from sqlalchemy import create_mock_engine
from sqlalchemy import event
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import testing
from sqlalchemy import text
from sqlalchemy.schema import AddConstraint
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.schema import DDL
from sqlalchemy.schema import DropConstraint
from sqlalchemy.testing import AssertsCompiledSQL
from sqlalchemy.testing import engines
from sqlalchemy.testing import eq_
from sqlalchemy.testing import fixtures
from sqlalchemy.testing.schema import Column
from sqlalchemy.testing.schema import Table


class DDLEventTest(fixtures.TestBase):
    def setup_test(self):
        self.bind = engines.mock_engine()
        self.metadata = MetaData()
        self.table = Table("t", self.metadata, Column("id", Integer))

    def test_table_create_before(self):
        table, bind = self.table, self.bind
        canary = mock.Mock()
        event.listen(table, "before_create", canary.before_create)

        table.create(bind)
        table.drop(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.before_create(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                )
            ],
        )

    def test_table_create_after(self):
        table, bind = self.table, self.bind
        canary = mock.Mock()
        event.listen(table, "after_create", canary.after_create)

        table.create(bind)
        table.drop(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.after_create(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                )
            ],
        )

    def test_table_create_both(self):
        table, bind = self.table, self.bind
        canary = mock.Mock()
        event.listen(table, "before_create", canary.before_create)
        event.listen(table, "after_create", canary.after_create)

        table.create(bind)
        table.drop(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.before_create(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                ),
                mock.call.after_create(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                ),
            ],
        )

    def test_table_drop_before(self):
        table, bind = self.table, self.bind
        canary = mock.Mock()
        event.listen(table, "before_drop", canary.before_drop)

        table.create(bind)
        table.drop(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.before_drop(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                )
            ],
        )

    def test_table_drop_after(self):
        table, bind = self.table, self.bind
        canary = mock.Mock()
        event.listen(table, "after_drop", canary.after_drop)

        table.create(bind)
        canary.state = "skipped"
        table.drop(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.after_drop(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                )
            ],
        )

    def test_table_drop_both(self):
        table, bind = self.table, self.bind
        canary = mock.Mock()

        event.listen(table, "before_drop", canary.before_drop)
        event.listen(table, "after_drop", canary.after_drop)

        table.create(bind)
        table.drop(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.before_drop(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                ),
                mock.call.after_drop(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                ),
            ],
        )

    def test_table_all(self):
        table, bind = self.table, self.bind
        canary = mock.Mock()

        event.listen(table, "before_create", canary.before_create)
        event.listen(table, "after_create", canary.after_create)
        event.listen(table, "before_drop", canary.before_drop)
        event.listen(table, "after_drop", canary.after_drop)

        table.create(bind)
        table.drop(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.before_create(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                ),
                mock.call.after_create(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                ),
                mock.call.before_drop(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                ),
                mock.call.after_drop(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                ),
            ],
        )

    def test_metadata_create_before(self):
        metadata, bind = self.metadata, self.bind
        canary = mock.Mock()
        event.listen(metadata, "before_create", canary.before_create)

        metadata.create_all(bind)
        metadata.drop_all(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.before_create(
                    # checkfirst is False because of the MockConnection
                    # used in the current testing strategy.
                    metadata,
                    self.bind,
                    checkfirst=False,
                    tables=list(metadata.tables.values()),
                    _ddl_runner=mock.ANY,
                )
            ],
        )

    def test_metadata_create_after(self):
        metadata, bind = self.metadata, self.bind
        canary = mock.Mock()
        event.listen(metadata, "after_create", canary.after_create)

        metadata.create_all(bind)
        metadata.drop_all(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.after_create(
                    metadata,
                    self.bind,
                    checkfirst=False,
                    tables=list(metadata.tables.values()),
                    _ddl_runner=mock.ANY,
                )
            ],
        )

    def test_metadata_create_both(self):
        metadata, bind = self.metadata, self.bind
        canary = mock.Mock()

        event.listen(metadata, "before_create", canary.before_create)
        event.listen(metadata, "after_create", canary.after_create)

        metadata.create_all(bind)
        metadata.drop_all(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.before_create(
                    metadata,
                    self.bind,
                    checkfirst=False,
                    tables=list(metadata.tables.values()),
                    _ddl_runner=mock.ANY,
                ),
                mock.call.after_create(
                    metadata,
                    self.bind,
                    checkfirst=False,
                    tables=list(metadata.tables.values()),
                    _ddl_runner=mock.ANY,
                ),
            ],
        )

    def test_metadata_drop_before(self):
        metadata, bind = self.metadata, self.bind
        canary = mock.Mock()
        event.listen(metadata, "before_drop", canary.before_drop)

        metadata.create_all(bind)
        metadata.drop_all(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.before_drop(
                    metadata,
                    self.bind,
                    checkfirst=False,
                    tables=list(metadata.tables.values()),
                    _ddl_runner=mock.ANY,
                )
            ],
        )

    def test_metadata_drop_after(self):
        metadata, bind = self.metadata, self.bind
        canary = mock.Mock()
        event.listen(metadata, "after_drop", canary.after_drop)

        metadata.create_all(bind)
        metadata.drop_all(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.after_drop(
                    metadata,
                    self.bind,
                    checkfirst=False,
                    tables=list(metadata.tables.values()),
                    _ddl_runner=mock.ANY,
                )
            ],
        )

    def test_metadata_drop_both(self):
        metadata, bind = self.metadata, self.bind
        canary = mock.Mock()

        event.listen(metadata, "before_drop", canary.before_drop)
        event.listen(metadata, "after_drop", canary.after_drop)

        metadata.create_all(bind)
        metadata.drop_all(bind)
        eq_(
            canary.mock_calls,
            [
                mock.call.before_drop(
                    metadata,
                    self.bind,
                    checkfirst=False,
                    tables=list(metadata.tables.values()),
                    _ddl_runner=mock.ANY,
                ),
                mock.call.after_drop(
                    metadata,
                    self.bind,
                    checkfirst=False,
                    tables=list(metadata.tables.values()),
                    _ddl_runner=mock.ANY,
                ),
            ],
        )

    def test_metadata_table_isolation(self):
        metadata, table = self.metadata, self.table
        table_canary = mock.Mock()
        metadata_canary = mock.Mock()

        event.listen(table, "before_create", table_canary.before_create)

        event.listen(metadata, "before_create", metadata_canary.before_create)
        self.table.create(self.bind)
        eq_(
            table_canary.mock_calls,
            [
                mock.call.before_create(
                    table,
                    self.bind,
                    checkfirst=False,
                    _ddl_runner=mock.ANY,
                    _is_metadata_operation=mock.ANY,
                )
            ],
        )
        eq_(metadata_canary.mock_calls, [])


class DDLExecutionTest(AssertsCompiledSQL, fixtures.TestBase):
    def setup_test(self):
        self.engine = engines.mock_engine()
        self.metadata = MetaData()
        self.users = Table(
            "users",
            self.metadata,
            Column("user_id", Integer, primary_key=True),
            Column("user_name", String(40)),
        )

    def test_table_standalone(self):
        users, engine = self.users, self.engine
        event.listen(users, "before_create", DDL("mxyzptlk"))
        event.listen(users, "after_create", DDL("klptzyxm"))
        event.listen(users, "before_drop", DDL("xyzzy"))
        event.listen(users, "after_drop", DDL("fnord"))

        users.create(self.engine)
        strings = [str(x) for x in engine.mock]
        assert "mxyzptlk" in strings
        assert "klptzyxm" in strings
        assert "xyzzy" not in strings
        assert "fnord" not in strings
        del engine.mock[:]
        users.drop(self.engine)
        strings = [str(x) for x in engine.mock]
        assert "mxyzptlk" not in strings
        assert "klptzyxm" not in strings
        assert "xyzzy" in strings
        assert "fnord" in strings

    def test_table_by_metadata(self):
        metadata, users, engine = self.metadata, self.users, self.engine

        event.listen(users, "before_create", DDL("mxyzptlk"))
        event.listen(users, "after_create", DDL("klptzyxm"))
        event.listen(users, "before_drop", DDL("xyzzy"))
        event.listen(users, "after_drop", DDL("fnord"))

        metadata.create_all(self.engine)
        strings = [str(x) for x in engine.mock]
        assert "mxyzptlk" in strings
        assert "klptzyxm" in strings
        assert "xyzzy" not in strings
        assert "fnord" not in strings
        del engine.mock[:]
        metadata.drop_all(self.engine)
        strings = [str(x) for x in engine.mock]
        assert "mxyzptlk" not in strings
        assert "klptzyxm" not in strings
        assert "xyzzy" in strings
        assert "fnord" in strings

    def test_metadata(self):
        metadata, engine = self.metadata, self.engine

        event.listen(metadata, "before_create", DDL("mxyzptlk"))
        event.listen(metadata, "after_create", DDL("klptzyxm"))
        event.listen(metadata, "before_drop", DDL("xyzzy"))
        event.listen(metadata, "after_drop", DDL("fnord"))

        metadata.create_all(self.engine)
        strings = [str(x) for x in engine.mock]
        assert "mxyzptlk" in strings
        assert "klptzyxm" in strings
        assert "xyzzy" not in strings
        assert "fnord" not in strings
        del engine.mock[:]
        metadata.drop_all(self.engine)
        strings = [str(x) for x in engine.mock]
        assert "mxyzptlk" not in strings
        assert "klptzyxm" not in strings
        assert "xyzzy" in strings
        assert "fnord" in strings

    def test_conditional_constraint(self):
        metadata, users = self.metadata, self.users
        nonpg_mock = engines.mock_engine(dialect_name="sqlite")
        pg_mock = engines.mock_engine(dialect_name="postgresql")
        constraint = CheckConstraint(
            "a < b", name="my_test_constraint", table=users
        )

        # by placing the constraint in an Add/Drop construct, the
        # 'inline_ddl' flag is set to False

        event.listen(
            users,
            "after_create",
            AddConstraint(constraint).execute_if(dialect="postgresql"),
        )

        event.listen(
            users,
            "before_drop",
            DropConstraint(constraint).execute_if(dialect="postgresql"),
        )

        metadata.create_all(bind=nonpg_mock)
        strings = " ".join(str(x) for x in nonpg_mock.mock)
        assert "my_test_constraint" not in strings
        metadata.drop_all(bind=nonpg_mock)
        strings = " ".join(str(x) for x in nonpg_mock.mock)
        assert "my_test_constraint" not in strings
        metadata.create_all(bind=pg_mock)
        strings = " ".join(str(x) for x in pg_mock.mock)
        assert "my_test_constraint" in strings
        metadata.drop_all(bind=pg_mock)
        strings = " ".join(str(x) for x in pg_mock.mock)
        assert "my_test_constraint" in strings

    @testing.combinations(("dialect",), ("callable",), ("callable_w_state",))
    def test_inline_ddl_if_dialect_name(self, ddl_if_type):
        nonpg_mock = engines.mock_engine(dialect_name="sqlite")
        pg_mock = engines.mock_engine(dialect_name="postgresql")

        metadata = MetaData()

        capture_mock = Mock()
        state = object()

        if ddl_if_type == "dialect":
            ddl_kwargs = dict(dialect="postgresql")
        elif ddl_if_type == "callable":

            def is_pg(ddl, target, bind, **kw):
                capture_mock.is_pg(ddl, target, bind, **kw)
                return kw["dialect"].name == "postgresql"

            ddl_kwargs = dict(callable_=is_pg)
        elif ddl_if_type == "callable_w_state":

            def is_pg(ddl, target, bind, **kw):
                capture_mock.is_pg(ddl, target, bind, **kw)
                return kw["dialect"].name == "postgresql"

            ddl_kwargs = dict(callable_=is_pg, state=state)
        else:
            assert False

        data_col = Column("data", String)
        t = Table(
            "a",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("num", Integer),
            data_col,
            Index("my_pg_index", data_col).ddl_if(**ddl_kwargs),
            CheckConstraint("num > 5").ddl_if(**ddl_kwargs),
        )

        metadata.create_all(nonpg_mock)
        eq_(len(nonpg_mock.mock), 1)
        self.assert_compile(
            nonpg_mock.mock[0],
            "CREATE TABLE a (id INTEGER NOT NULL, num INTEGER, "
            "data VARCHAR, PRIMARY KEY (id))",
            dialect=nonpg_mock.dialect,
        )

        metadata.create_all(pg_mock)

        eq_(len(pg_mock.mock), 2)

        self.assert_compile(
            pg_mock.mock[0],
            "CREATE TABLE a (id SERIAL NOT NULL, num INTEGER, "
            "data VARCHAR, PRIMARY KEY (id), CHECK (num > 5))",
            dialect=pg_mock.dialect,
        )
        self.assert_compile(
            pg_mock.mock[1],
            "CREATE INDEX my_pg_index ON a (data)",
            dialect="postgresql",
        )

        the_index = list(t.indexes)[0]
        the_constraint = list(
            c for c in t.constraints if isinstance(c, CheckConstraint)
        )[0]

        if ddl_if_type in ("callable", "callable_w_state"):

            if ddl_if_type == "callable":
                check_state = None
            else:
                check_state = state

            eq_(
                capture_mock.mock_calls,
                [
                    mock.call.is_pg(
                        mock.ANY,
                        the_index,
                        mock.ANY,
                        state=check_state,
                        dialect=nonpg_mock.dialect,
                        compiler=None,
                    ),
                    mock.call.is_pg(
                        mock.ANY,
                        the_constraint,
                        None,
                        state=check_state,
                        dialect=nonpg_mock.dialect,
                        compiler=mock.ANY,
                    ),
                    mock.call.is_pg(
                        mock.ANY,
                        the_index,
                        mock.ANY,
                        state=check_state,
                        dialect=pg_mock.dialect,
                        compiler=None,
                    ),
                    mock.call.is_pg(
                        mock.ANY,
                        the_constraint,
                        None,
                        state=check_state,
                        dialect=pg_mock.dialect,
                        compiler=mock.ANY,
                    ),
                ],
            )

    @testing.requires.sqlite
    def test_ddl_execute(self):
        engine = create_engine("sqlite:///")
        cx = engine.connect()
        cx.begin()
        ddl = DDL("SELECT 1")

        r = cx.execute(ddl)
        eq_(list(r), [(1,)])

    def test_platform_escape(self):
        """test the escaping of % characters in the DDL construct."""

        default_from = testing.db.dialect.statement_compiler(
            testing.db.dialect, None
        ).default_from()

        # We're abusing the DDL()
        # construct here by pushing a SELECT through it
        # so that we can verify the round trip.
        # the DDL() will trigger autocommit, which prohibits
        # some DBAPIs from returning results (pyodbc), so we
        # run in an explicit transaction.
        with testing.db.begin() as conn:
            eq_(
                conn.execute(
                    text("select 'foo%something'" + default_from)
                ).scalar(),
                "foo%something",
            )

            eq_(
                conn.execute(
                    DDL("select 'foo%%something'" + default_from)
                ).scalar(),
                "foo%something",
            )


class DDLTransactionTest(fixtures.TestBase):
    """test DDL transactional behavior as of SQLAlchemy 1.4."""

    @testing.fixture
    def metadata_fixture(self):
        m = MetaData()
        Table("t1", m, Column("q", Integer))
        Table("t2", m, Column("q", Integer))

        try:
            yield m
        finally:
            m.drop_all(testing.db)

    @testing.fixture
    def listening_engine_fixture(self):
        eng = engines.testing_engine()

        m1 = mock.Mock()

        event.listen(eng, "begin", m1.begin)
        event.listen(eng, "commit", m1.commit)
        event.listen(eng, "rollback", m1.rollback)

        @event.listens_for(eng, "before_cursor_execute")
        def before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            if "CREATE TABLE" in statement:
                m1.cursor_execute("CREATE TABLE ...")

        eng.connect().close()

        return eng, m1

    def test_ddl_engine(self, metadata_fixture, listening_engine_fixture):
        eng, m1 = listening_engine_fixture

        metadata_fixture.create_all(eng)

        eq_(
            m1.mock_calls,
            [
                mock.call.begin(mock.ANY),
                mock.call.cursor_execute("CREATE TABLE ..."),
                mock.call.cursor_execute("CREATE TABLE ..."),
                mock.call.commit(mock.ANY),
            ],
        )

    def test_ddl_connection_autobegin_transaction(
        self, metadata_fixture, listening_engine_fixture
    ):
        eng, m1 = listening_engine_fixture

        with eng.connect() as conn:
            metadata_fixture.create_all(conn)

            conn.commit()

        eq_(
            m1.mock_calls,
            [
                mock.call.begin(mock.ANY),
                mock.call.cursor_execute("CREATE TABLE ..."),
                mock.call.cursor_execute("CREATE TABLE ..."),
                mock.call.commit(mock.ANY),
            ],
        )

    def test_ddl_connection_explicit_begin_transaction(
        self, metadata_fixture, listening_engine_fixture
    ):
        eng, m1 = listening_engine_fixture

        with eng.connect() as conn:
            with conn.begin():
                metadata_fixture.create_all(conn)

        eq_(
            m1.mock_calls,
            [
                mock.call.begin(mock.ANY),
                mock.call.cursor_execute("CREATE TABLE ..."),
                mock.call.cursor_execute("CREATE TABLE ..."),
                mock.call.commit(mock.ANY),
            ],
        )


class DDLTest(fixtures.TestBase, AssertsCompiledSQL):
    def mock_engine(self):
        def executor(*a, **kw):
            return None

        engine = create_mock_engine(testing.db.name + "://", executor)
        # fmt: off
        engine.dialect.identifier_preparer = \
            tsa.sql.compiler.IdentifierPreparer(
                engine.dialect
            )
        # fmt: on
        return engine

    def test_tokens(self):
        m = MetaData()
        sane_alone = Table("t", m, Column("id", Integer))
        sane_schema = Table("t", m, Column("id", Integer), schema="s")
        insane_alone = Table("t t", m, Column("id", Integer))
        insane_schema = Table("t t", m, Column("id", Integer), schema="s s")
        ddl = DDL("%(schema)s-%(table)s-%(fullname)s")
        dialect = self.mock_engine().dialect
        self.assert_compile(ddl.against(sane_alone), "-t-t", dialect=dialect)
        self.assert_compile(
            ddl.against(sane_schema), "s-t-s.t", dialect=dialect
        )
        self.assert_compile(
            ddl.against(insane_alone), '-"t t"-"t t"', dialect=dialect
        )
        self.assert_compile(
            ddl.against(insane_schema),
            '"s s"-"t t"-"s s"."t t"',
            dialect=dialect,
        )

        # overrides are used piece-meal and verbatim.

        ddl = DDL(
            "%(schema)s-%(table)s-%(fullname)s-%(bonus)s",
            context={"schema": "S S", "table": "T T", "bonus": "b"},
        )
        self.assert_compile(
            ddl.against(sane_alone), "S S-T T-t-b", dialect=dialect
        )
        self.assert_compile(
            ddl.against(sane_schema), "S S-T T-s.t-b", dialect=dialect
        )
        self.assert_compile(
            ddl.against(insane_alone), 'S S-T T-"t t"-b', dialect=dialect
        )
        self.assert_compile(
            ddl.against(insane_schema),
            'S S-T T-"s s"."t t"-b',
            dialect=dialect,
        )

    def test_filter(self):
        cx = self.mock_engine()

        tbl = Table("t", MetaData(), Column("id", Integer))
        target = cx.name

        assert DDL("")._should_execute(tbl, cx)
        assert DDL("").execute_if(dialect=target)._should_execute(tbl, cx)
        assert not DDL("").execute_if(dialect="bogus")._should_execute(tbl, cx)
        assert (
            DDL("")
            .execute_if(callable_=lambda d, y, z, **kw: True)
            ._should_execute(tbl, cx)
        )
        assert (
            DDL("")
            .execute_if(
                callable_=lambda d, y, z, **kw: z.engine.name != "bogus"
            )
            ._should_execute(tbl, cx)
        )
