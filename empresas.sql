CREATE TABLE Empleados (
  empleado_id INT PRIMARY KEY,
  nombre VARCHAR(50),
  empresa_id INT,
  FOREIGN KEY (empresa_id) REFERENCES Empresas(empresa_id)
);


CREATE TABLE Empresas (
  empresa_id INT PRIMARY KEY,
  nombre VARCHAR(50),
  ciudad_id INT,
  FOREIGN KEY (ciudad_id) REFERENCES Ciudades(ciudad_id)
);

CREATE TABLE Ciudades (
  ciudad_id INT PRIMARY KEY,
  nombre VARCHAR(50),
  departamento_id INT,
  FOREIGN KEY (departamento_id) REFERENCES Departamentos(departamento_id)
);

CREATE TABLE Departamentos (
  departamento_id INT PRIMARY KEY,
  nombre VARCHAR(50),
  pais_id INT,
  FOREIGN KEY (pais_id) REFERENCES Paises(pais_id)
);

CREATE TABLE Paises (
  pais_id INT PRIMARY KEY,
  nombre VARCHAR(50)
);


CREATE TABLE EmpleadoEmpresa (
  id_emp_emp au
  empleado_id INT,
  empresa_id INT,
  fecha date,
  FOREIGN KEY (empleado_id) REFERENCES Empleados(empleado_id),
  FOREIGN KEY (empresa_id) REFERENCES Empresas(empresa_id),
  PRIMARY KEY (empleado_id, empresa_id)
);


CREATE TABLE Empresas (
  empresa_id INT PRIMARY KEY,
  nom_empresa VARCHAR(50),
  ciudad_id INT,
  rut BLOB,
  cedula_representante BLOB,
  otros_documentos BLOB,
  FOREIGN KEY (ciudad_id) REFERENCES Ciudades(ciudad_id)
);