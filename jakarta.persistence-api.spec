Name:		jakarta.persistence-api
Version:	2.2.3
Release:	1
Summary:	Jakarta Persistence 2.2 API
Group:		Development/Java
License:	EPL-2.0 OR BSD-3-Clause
URL:		https://projects.eclipse.org/projects/ee4j.jpa
Source0:	https://repo1.maven.org/maven2/jakarta/persistence/jakarta.persistence-api/%{version}/jakarta.persistence-api-%{version}-sources.jar
# 2.2.3 has no git tag. These texts are the 2.2.2 project license, and the sources use the same SPDX line.
Source1:	https://raw.githubusercontent.com/eclipse-ee4j/jpa-api/2.2.2-RELEASE/LICENSE.md#/jakarta.persistence-api-%{version}-LICENSE.md
Source2:	https://raw.githubusercontent.com/eclipse-ee4j/jpa-api/2.2.2-RELEASE/NOTICE.md#/jakarta.persistence-api-%{version}-NOTICE.md

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name %{name} --alias javax.persistence:javax.persistence-api

%description
Jakarta Persistence 2.2.3. The Java packages are still
javax.persistence. This jar also provides
javax.persistence:javax.persistence-api. PersistenceUnitInfo uses
javax.sql.DataSource from the JDK. The persistence and orm schemas
from 1.0 through 2.2 are included. There is no parent POM. This build
targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
rm -rf META-INF
cp -p %{SOURCE1} LICENSE
cp -p %{SOURCE2} NOTICE
mkdir -p src/main/java src/main/resources
python - <<'PY'
import shutil
from pathlib import Path

root = Path("javax")
if not root.is_dir():
    raise SystemExit("missing javax sources")
java_root = Path("src/main/java")
res_root = Path("src/main/resources")
for path in root.rglob("*"):
    if not path.is_file():
        continue
    rel = path.relative_to(root)
    if path.suffix == ".java":
        dest = java_root / "javax" / rel
    else:
        dest = res_root / "javax" / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(path, dest)
shutil.rmtree(root)
javas = list(java_root.rglob("*.java"))
if len(javas) != 192:
    raise SystemExit("java files " + str(len(javas)))
for name in ("EntityManager.java", "spi/PersistenceProvider.java", "spi/PersistenceUnitInfo.java"):
    if not (java_root / "javax/persistence" / name).is_file():
        raise SystemExit("missing " + name)
files = [path for path in res_root.rglob("*") if path.is_file()]
xsds = [path for path in files if path.suffix == ".xsd"]
if len(xsds) != 8 or len(files) != 8:
    raise SystemExit("schema count changed")
for name in ("persistence_2_2.xsd", "orm_2_2.xsd", "persistence_1_0.xsd", "orm_1_0.xsd"):
    if not (res_root / "javax/persistence" / name).is_file():
        raise SystemExit("missing " + name)
if list(Path(".").rglob("module-info.java")):
    raise SystemExit("module-info appeared")
header = (java_root / "javax/persistence/EntityManager.java").read_text(encoding="utf-8")
if "SPDX-License-Identifier: EPL-2.0 OR BSD-3-Clause" not in header:
    raise SystemExit("source license header changed")
license_text = Path("LICENSE").read_text(encoding="utf-8")
if "Eclipse Public License" not in license_text:
    raise SystemExit("LICENSE is not the EPL 2.0 text")
notice = Path("NOTICE").read_text(encoding="utf-8")
if "Eclipse Project for JPA" not in notice or "Eclipse Distribution License" not in notice or "EPL-2.0 OR BSD-3-Clause" not in notice:
    raise SystemExit("NOTICE is not the dual EPL and EDL grant")
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>jakarta.persistence</groupId>
  <artifactId>jakarta.persistence-api</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>Jakarta Persistence</name>
  <description>Jakarta Persistence %{version} API, packaged without a parent POM.</description>
  <url>https://projects.eclipse.org/projects/ee4j.jpa</url>
  <licenses>
    <license>
      <name>EPL-2.0 OR BSD-3-Clause</name>
      <url>https://www.eclipse.org/legal/epl-2.0/</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
        <configuration>
          <archive>
            <manifestEntries>
              <Automatic-Module-Name>java.persistence</Automatic-Module-Name>
              <Specification-Version>2.2</Specification-Version>
              <Implementation-Version>%{version}</Implementation-Version>
            </manifestEntries>
          </archive>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>jakarta.persistence-api</artifactId>",
    "<Automatic-Module-Name>java.persistence</Automatic-Module-Name>",
    "<version>%{version}</version>",
    "<release>8</release>",
    "</project.build.sourceEncoding>",
    "<Specification-Version>2.2</Specification-Version>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
if pom.count("<version>2.2.3</version>") != 1:
    raise SystemExit("version 2.2.3 count")
if "<dependencies>" in pom:
    raise SystemExit("pom grew a dependency")
for needle in (
    "junit",
    "SNAPSHOT",
    "<source>",
    "<target>",
    "<parent>",
    "<groupId>org.eclipse.ee4j</groupId>",
    "jvnet",
    "felix",
    "maven-bundle-plugin",
    "<version>2.2</version>",
    "projectbuild.sourceEncoding",
):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/jakarta.persistence-api-%{version}.jar --describe-module java.persistence > module-describe.txt
grep -q '^java\.persistence@' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }
python - <<'PY'
import struct
import zipfile
from pathlib import Path
jar = Path("target/jakarta.persistence-api-%{version}.jar")
with zipfile.ZipFile(jar) as zf:
    names = set(zf.namelist())
    required = {
        "javax/persistence/Access.class",
        "javax/persistence/AccessType.class",
        "javax/persistence/AssociationOverride.class",
        "javax/persistence/AssociationOverrides.class",
        "javax/persistence/AttributeConverter.class",
        "javax/persistence/AttributeNode.class",
        "javax/persistence/AttributeOverride.class",
        "javax/persistence/AttributeOverrides.class",
        "javax/persistence/Basic.class",
        "javax/persistence/Cache.class",
        "javax/persistence/CacheRetrieveMode.class",
        "javax/persistence/CacheStoreMode.class",
        "javax/persistence/Cacheable.class",
        "javax/persistence/CascadeType.class",
        "javax/persistence/CollectionTable.class",
        "javax/persistence/Column.class",
        "javax/persistence/ColumnResult.class",
        "javax/persistence/ConstraintMode.class",
        "javax/persistence/ConstructorResult.class",
        "javax/persistence/Convert.class",
        "javax/persistence/Converter.class",
        "javax/persistence/Converts.class",
        "javax/persistence/DiscriminatorColumn.class",
        "javax/persistence/DiscriminatorType.class",
        "javax/persistence/DiscriminatorValue.class",
        "javax/persistence/ElementCollection.class",
        "javax/persistence/Embeddable.class",
        "javax/persistence/Embedded.class",
        "javax/persistence/EmbeddedId.class",
        "javax/persistence/Entity.class",
        "javax/persistence/EntityExistsException.class",
        "javax/persistence/EntityGraph.class",
        "javax/persistence/EntityListeners.class",
        "javax/persistence/EntityManager.class",
        "javax/persistence/EntityManagerFactory.class",
        "javax/persistence/EntityNotFoundException.class",
        "javax/persistence/EntityResult.class",
        "javax/persistence/EntityTransaction.class",
        "javax/persistence/EnumType.class",
        "javax/persistence/Enumerated.class",
        "javax/persistence/ExcludeDefaultListeners.class",
        "javax/persistence/ExcludeSuperclassListeners.class",
        "javax/persistence/FetchType.class",
        "javax/persistence/FieldResult.class",
        "javax/persistence/FlushModeType.class",
        "javax/persistence/ForeignKey.class",
        "javax/persistence/GeneratedValue.class",
        "javax/persistence/GenerationType.class",
        "javax/persistence/Id.class",
        "javax/persistence/IdClass.class",
        "javax/persistence/Index.class",
        "javax/persistence/Inheritance.class",
        "javax/persistence/InheritanceType.class",
        "javax/persistence/JoinColumn.class",
        "javax/persistence/JoinColumns.class",
        "javax/persistence/JoinTable.class",
        "javax/persistence/Lob.class",
        "javax/persistence/LockModeType.class",
        "javax/persistence/LockTimeoutException.class",
        "javax/persistence/ManyToMany.class",
        "javax/persistence/ManyToOne.class",
        "javax/persistence/MapKey.class",
        "javax/persistence/MapKeyClass.class",
        "javax/persistence/MapKeyColumn.class",
        "javax/persistence/MapKeyEnumerated.class",
        "javax/persistence/MapKeyJoinColumn.class",
        "javax/persistence/MapKeyJoinColumns.class",
        "javax/persistence/MapKeyTemporal.class",
        "javax/persistence/MappedSuperclass.class",
        "javax/persistence/MapsId.class",
        "javax/persistence/NamedAttributeNode.class",
        "javax/persistence/NamedEntityGraph.class",
        "javax/persistence/NamedEntityGraphs.class",
        "javax/persistence/NamedNativeQueries.class",
        "javax/persistence/NamedNativeQuery.class",
        "javax/persistence/NamedQueries.class",
        "javax/persistence/NamedQuery.class",
        "javax/persistence/NamedStoredProcedureQueries.class",
        "javax/persistence/NamedStoredProcedureQuery.class",
        "javax/persistence/NamedSubgraph.class",
        "javax/persistence/NoResultException.class",
        "javax/persistence/NonUniqueResultException.class",
        "javax/persistence/OneToMany.class",
        "javax/persistence/OneToOne.class",
        "javax/persistence/OptimisticLockException.class",
        "javax/persistence/OrderBy.class",
        "javax/persistence/OrderColumn.class",
        "javax/persistence/Parameter.class",
        "javax/persistence/ParameterMode.class",
        "javax/persistence/Persistence$1.class",
        "javax/persistence/Persistence$PersistenceUtilImpl.class",
        "javax/persistence/Persistence.class",
        "javax/persistence/PersistenceContext.class",
        "javax/persistence/PersistenceContextType.class",
        "javax/persistence/PersistenceContexts.class",
        "javax/persistence/PersistenceException.class",
        "javax/persistence/PersistenceProperty.class",
        "javax/persistence/PersistenceUnit.class",
        "javax/persistence/PersistenceUnitUtil.class",
        "javax/persistence/PersistenceUnits.class",
        "javax/persistence/PersistenceUtil.class",
        "javax/persistence/PessimisticLockException.class",
        "javax/persistence/PessimisticLockScope.class",
        "javax/persistence/PostLoad.class",
        "javax/persistence/PostPersist.class",
        "javax/persistence/PostRemove.class",
        "javax/persistence/PostUpdate.class",
        "javax/persistence/PrePersist.class",
        "javax/persistence/PreRemove.class",
        "javax/persistence/PreUpdate.class",
        "javax/persistence/PrimaryKeyJoinColumn.class",
        "javax/persistence/PrimaryKeyJoinColumns.class",
        "javax/persistence/Query.class",
        "javax/persistence/QueryHint.class",
        "javax/persistence/QueryTimeoutException.class",
        "javax/persistence/RollbackException.class",
        "javax/persistence/SecondaryTable.class",
        "javax/persistence/SecondaryTables.class",
        "javax/persistence/SequenceGenerator.class",
        "javax/persistence/SequenceGenerators.class",
        "javax/persistence/SharedCacheMode.class",
        "javax/persistence/SqlResultSetMapping.class",
        "javax/persistence/SqlResultSetMappings.class",
        "javax/persistence/StoredProcedureParameter.class",
        "javax/persistence/StoredProcedureQuery.class",
        "javax/persistence/Subgraph.class",
        "javax/persistence/SynchronizationType.class",
        "javax/persistence/Table.class",
        "javax/persistence/TableGenerator.class",
        "javax/persistence/TableGenerators.class",
        "javax/persistence/Temporal.class",
        "javax/persistence/TemporalType.class",
        "javax/persistence/TransactionRequiredException.class",
        "javax/persistence/Transient.class",
        "javax/persistence/Tuple.class",
        "javax/persistence/TupleElement.class",
        "javax/persistence/TypedQuery.class",
        "javax/persistence/UniqueConstraint.class",
        "javax/persistence/ValidationMode.class",
        "javax/persistence/Version.class",
        "javax/persistence/criteria/AbstractQuery.class",
        "javax/persistence/criteria/CollectionJoin.class",
        "javax/persistence/criteria/CommonAbstractCriteria.class",
        "javax/persistence/criteria/CompoundSelection.class",
        "javax/persistence/criteria/CriteriaBuilder$Case.class",
        "javax/persistence/criteria/CriteriaBuilder$Coalesce.class",
        "javax/persistence/criteria/CriteriaBuilder$In.class",
        "javax/persistence/criteria/CriteriaBuilder$SimpleCase.class",
        "javax/persistence/criteria/CriteriaBuilder$Trimspec.class",
        "javax/persistence/criteria/CriteriaBuilder.class",
        "javax/persistence/criteria/CriteriaDelete.class",
        "javax/persistence/criteria/CriteriaQuery.class",
        "javax/persistence/criteria/CriteriaUpdate.class",
        "javax/persistence/criteria/Expression.class",
        "javax/persistence/criteria/Fetch.class",
        "javax/persistence/criteria/FetchParent.class",
        "javax/persistence/criteria/From.class",
        "javax/persistence/criteria/Join.class",
        "javax/persistence/criteria/JoinType.class",
        "javax/persistence/criteria/ListJoin.class",
        "javax/persistence/criteria/MapJoin.class",
        "javax/persistence/criteria/Order.class",
        "javax/persistence/criteria/ParameterExpression.class",
        "javax/persistence/criteria/Path.class",
        "javax/persistence/criteria/PluralJoin.class",
        "javax/persistence/criteria/Predicate$BooleanOperator.class",
        "javax/persistence/criteria/Predicate.class",
        "javax/persistence/criteria/Root.class",
        "javax/persistence/criteria/Selection.class",
        "javax/persistence/criteria/SetJoin.class",
        "javax/persistence/criteria/Subquery.class",
        "javax/persistence/metamodel/Attribute$PersistentAttributeType.class",
        "javax/persistence/metamodel/Attribute.class",
        "javax/persistence/metamodel/BasicType.class",
        "javax/persistence/metamodel/Bindable$BindableType.class",
        "javax/persistence/metamodel/Bindable.class",
        "javax/persistence/metamodel/CollectionAttribute.class",
        "javax/persistence/metamodel/EmbeddableType.class",
        "javax/persistence/metamodel/EntityType.class",
        "javax/persistence/metamodel/IdentifiableType.class",
        "javax/persistence/metamodel/ListAttribute.class",
        "javax/persistence/metamodel/ManagedType.class",
        "javax/persistence/metamodel/MapAttribute.class",
        "javax/persistence/metamodel/MappedSuperclassType.class",
        "javax/persistence/metamodel/Metamodel.class",
        "javax/persistence/metamodel/PluralAttribute$CollectionType.class",
        "javax/persistence/metamodel/PluralAttribute.class",
        "javax/persistence/metamodel/SetAttribute.class",
        "javax/persistence/metamodel/SingularAttribute.class",
        "javax/persistence/metamodel/StaticMetamodel.class",
        "javax/persistence/metamodel/Type$PersistenceType.class",
        "javax/persistence/metamodel/Type.class",
        "javax/persistence/spi/ClassTransformer.class",
        "javax/persistence/spi/LoadState.class",
        "javax/persistence/spi/PersistenceProvider.class",
        "javax/persistence/spi/PersistenceProviderResolver.class",
        "javax/persistence/spi/PersistenceProviderResolverHolder$1.class",
        "javax/persistence/spi/PersistenceProviderResolverHolder$DefaultPersistenceProviderResolver$1.class",
        "javax/persistence/spi/PersistenceProviderResolverHolder$DefaultPersistenceProviderResolver$CacheKey.class",
        "javax/persistence/spi/PersistenceProviderResolverHolder$DefaultPersistenceProviderResolver$CacheKeyReference.class",
        "javax/persistence/spi/PersistenceProviderResolverHolder$DefaultPersistenceProviderResolver$LoaderReference.class",
        "javax/persistence/spi/PersistenceProviderResolverHolder$DefaultPersistenceProviderResolver$PersistenceProviderReference.class",
        "javax/persistence/spi/PersistenceProviderResolverHolder$DefaultPersistenceProviderResolver.class",
        "javax/persistence/spi/PersistenceProviderResolverHolder.class",
        "javax/persistence/spi/PersistenceUnitInfo.class",
        "javax/persistence/spi/PersistenceUnitTransactionType.class",
        "javax/persistence/spi/ProviderUtil.class",
    }
    allowed = {
        "javax/persistence/package-info.class",
        "javax/persistence/criteria/package-info.class",
        "javax/persistence/metamodel/package-info.class",
        "javax/persistence/spi/package-info.class",
    }
    classes = {name for name in names if name.endswith(".class")}
    missing = sorted(required - classes)
    extra = sorted(classes - required - allowed)
    if missing or extra:
        raise SystemExit("class set mismatch missing=" + " ".join(missing) + " extra=" + " ".join(extra))
    if any(name.endswith("module-info.class") for name in classes):
        raise SystemExit("module-info appeared")
    xsds = sorted(name for name in names if name.endswith(".xsd"))
    if xsds != [
        "javax/persistence/orm_1_0.xsd",
        "javax/persistence/orm_2_0.xsd",
        "javax/persistence/orm_2_1.xsd",
        "javax/persistence/orm_2_2.xsd",
        "javax/persistence/persistence_1_0.xsd",
        "javax/persistence/persistence_2_0.xsd",
        "javax/persistence/persistence_2_1.xsd",
        "javax/persistence/persistence_2_2.xsd",
    ]:
        raise SystemExit("schemas changed")
    data = zf.read("javax/persistence/EntityManager.class")
    if data[:4] != b"\xca\xfe\xba\xbe":
        raise SystemExit("EntityManager is not a class")
    major = struct.unpack(">H", data[6:8])[0]
    if major != 52:
        raise SystemExit("EntityManager class version " + str(major))
    info = zf.read("javax/persistence/spi/PersistenceUnitInfo.class")
    if b"javax/sql/DataSource" not in info:
        raise SystemExit("PersistenceUnitInfo lost DataSource")
PY

%files -f .mfiles
%doc LICENSE NOTICE
