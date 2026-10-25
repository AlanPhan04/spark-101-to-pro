import org.apache.spark.SparkConf
import org.apache.spark.serializer.{JavaSerializer, KryoSerializer}
val conf = new SparkConf()
val data = (1 to 20000).map(i => ("o" + i, 1772323200000L + i, "p%07d".format(i % 5000), i * 1.5, i % 7)).toArray
val js = new JavaSerializer(conf).newInstance(); val ks = new KryoSerializer(conf).newInstance()
var jEach = 0L; var kEach = 0L
for (o <- data) { jEach += js.serialize(o).limit(); kEach += ks.serialize(o).limit() }
val jArr = js.serialize(data).limit(); val kArr = ks.serialize(data).limit()
println(s"RESULT n=${data.length} java_each=$jEach kryo_each=$kEach java_array=$jArr kryo_array=$kArr")
System.exit(0)
