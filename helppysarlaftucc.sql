CREATE DATABASE helppysarlaftucc;

USE helppysarlaftucc;

CREATE TABLE ciudades (
  `ciudad_id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `departamento_id` int(11) NOT NULL
) ;

CREATE TABLE `departamentos` (
  `departamento_id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `pais_id` int(11) NOT NULL
) ;

CREATE TABLE `paises` (
  `pais_id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL
) ;

CREATE TABLE `empleadoempresa` (
  `id_empr_empl` int(11) NOT NULL,
  `empleado_id` int(11) NOT NULL,
  `empresa_id` int(11) NOT NULL,
  `fecha_veri` date NOT NULL,
  `comentario` varchar(100) NOT NULL
);

CREATE TABLE tipos_documento (
  tipo_documento_id INT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL
);

CREATE TABLE empleados (
  empleado_id INT PRIMARY KEY,
  pri_nom VARCHAR(50) DEFAULT NULL,
  seg_nombre VARCHAR(50) DEFAULT NULL,
  empresa_id INT DEFAULT NULL,
  tipo_documento_id INT,
  documento VARCHAR(50) DEFAULT NULL,
  primer_apellido VARCHAR(50) DEFAULT NULL,
  segundo_apellido VARCHAR(50) DEFAULT NULL,
  FOREIGN KEY (tipo_documento_id) REFERENCES tipos_documento(tipo_documento_id)
);


CREATE TABLE telefonos (
  telefono_id INT PRIMARY KEY,
  empleado_id INT NOT NULL,
  telefono VARCHAR(20) NOT NULL,
  ciudad_id int(11) NOT NULL,
  FOREIGN KEY (empleado_id) REFERENCES empleados(empleado_id)
);

CREATE TABLE direcciones (
  direccion_id INT PRIMARY KEY,
  empleado_id INT NOT NULL,
  direccion VARCHAR(100) NOT NULL,
  ciudad_id int(11) NOT NULL,
  FOREIGN KEY (empleado_id) REFERENCES empleados(empleado_id)
);

CREATE TABLE `empresas` (
  `empresa_id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `ciudad_id` int(11) NOT NULL
) ;

CREATE TABLE `relacionada` (
  `id_relacion` int(11) NOT NULL,
  `empresa_padre_id` int(11) NOT NULL,
  `empresa_hija_id` int(11) NOT NULL,
  `fecha_revison` date DEFAULT NULL,
  `comentario` varchar(100) DEFAULT NULL
);

CREATE TABLE informes (
  informe_id INT PRIMARY KEY,
  fecha DATE,
  hora TIME,
  empresa_id INT,
  empleado_id INT
);

CREATE TABLE tipos_documento_adjunto (
  tipo_documento_id INT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL
);

CREATE TABLE documentos_adjuntos (
  documento_id INT PRIMARY KEY,
  informe_id INT,
  tipo_documento_adjunto int NOT NULL,
  archivo_adjunto BLOB NOT NULL
);


CREATE TABLE procesos_autoevaluacion (
  proceso_id INT PRIMARY KEY,
  empresa_id INT,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL
  -- Otros campos relevantes para el proceso de autoevaluación
  
);

CREATE TABLE preguntas (
  pregunta_id INT PRIMARY KEY,
  enunciado VARCHAR(100) NOT NULL,
  fecha_creada date NOT NULL
  -- Otros campos relevantes para la pregunta
);

CREATE TABLE items (
  item_id INT PRIMARY KEY,
  descripcion VARCHAR(100) NOT NULL,
  fecha_creada date NOT NULL
  -- Otros campos relevantes para el ítem
);

CREATE TABLE respuestas_autoevaluacion (
  proceso_id INT,
  pregunta_id INT,
  item_id INT,
  valor INT,
  PRIMARY KEY (proceso_id, pregunta_id, item_id),
  FOREIGN KEY (proceso_id) REFERENCES procesos_autoevaluacion(proceso_id),
  FOREIGN KEY (pregunta_id) REFERENCES preguntas(pregunta_id),
  FOREIGN KEY (item_id) REFERENCES items(item_id)
);




ALTER TABLE `ciudades`
  ADD PRIMARY KEY (`ciudad_id`),
  ADD KEY `departamento_id` (`departamento_id`);


ALTER TABLE `departamentos`
  ADD PRIMARY KEY (`departamento_id`),
  ADD KEY `pais_id` (`pais_id`);

ALTER TABLE `empleadoempresa`
  ADD PRIMARY KEY (`id_empr_empl`,`empleado_id`,`empresa_id`),
  ADD KEY `empleado_id` (`empleado_id`),
  ADD KEY `empresa_id` (`empresa_id`);

ALTER TABLE `empresas`
  ADD PRIMARY KEY (`empresa_id`),
  ADD KEY `ciudad_id` (`ciudad_id`);

ALTER TABLE `paises`
  ADD PRIMARY KEY (`pais_id`);

ALTER TABLE `relacionada`
  ADD PRIMARY KEY (`id_relacion`,`empresa_padre_id`,`empresa_hija_id`),
  ADD KEY `empresa_padre_id` (`empresa_padre_id`),
  ADD KEY `empresa_hija_id` (`empresa_hija_id`);

ALTER TABLE `empleadoempresa`
  MODIFY `id_empr_empl` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `relacionada`
  MODIFY `id_relacion` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `ciudades`
  ADD CONSTRAINT `ciudades_ibfk_1` FOREIGN KEY (`departamento_id`) REFERENCES `departamentos` (`departamento_id`);

ALTER TABLE `departamentos`
  ADD CONSTRAINT `departamentos_ibfk_1` FOREIGN KEY (`pais_id`) REFERENCES `paises` (`pais_id`);

ALTER TABLE `empleadoempresa`
  ADD CONSTRAINT `empleadoempresa_ibfk_1` FOREIGN KEY (`empleado_id`) REFERENCES `empleados` (`empleado_id`),
  ADD CONSTRAINT `empleadoempresa_ibfk_2` FOREIGN KEY (`empresa_id`) REFERENCES `empresas` (`empresa_id`);

ALTER TABLE `empresas`
  ADD CONSTRAINT `empresas_ibfk_1` FOREIGN KEY (`ciudad_id`) REFERENCES `ciudades` (`ciudad_id`);

ALTER TABLE `relacionada`
  ADD CONSTRAINT `relacionada_ibfk_1` FOREIGN KEY (`empresa_padre_id`) REFERENCES `empresas` (`empresa_id`),
  ADD CONSTRAINT `relacionada_ibfk_2` FOREIGN KEY (`empresa_hija_id`) REFERENCES `empresas` (`empresa_id`);

ALTER TABLE `telefonos`
  ADD CONSTRAINT `telefonosemp_ibfk_1` FOREIGN KEY (`ciudad_id`) REFERENCES `ciudades` (`ciudad_id`);

ALTER TABLE `direcciones`
  ADD CONSTRAINT `direccionesemp_ibfk_1` FOREIGN KEY (`ciudad_id`) REFERENCES `ciudades` (`ciudad_id`);

ALTER TABLE `informes`
  ADD CONSTRAINT `empresa_informe` FOREIGN KEY (`empresa_id`) REFERENCES `empresas`(`empresa_id`),
  ADD CONSTRAINT `empresa_informe1`  FOREIGN KEY (`empleado_id`) REFERENCES `empleados`(`empleado_id`);

ALTER TABLE `procesos_autoevaluacion`
  ADD CONSTRAINT `procesos_autoevaluacion12` FOREIGN KEY (`empresa_id`) REFERENCES `empresas`(`empresa_id`);

ALTER TABLE `documentos_adjuntos`
    ADD CONSTRAINT `documentos_adjuntos1` FOREIGN KEY (`tipo_documento_adjunto`) REFERENCES `tipos_documento_adjunto`(`tipo_documento_id`),
    ADD CONSTRAINT `documentos_adjuntos2` FOREIGN KEY (`informe_id`) REFERENCES `informes`(`informe_id`);


COMMIT;

