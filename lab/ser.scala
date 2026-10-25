import org.apache.spark.SparkConf
import org.apache.spark.serializer.{JavaSerializer, KryoSerializer}
val conf = new SparkConf().set("spark.kryo.registrationRequired", "false")
case class Order(id: String, ts: Long, product: String, total: Double, days: Int)
val data = (1 to 100000).map(i => Order("o" + i, 1772323200000L + i, "p%07d".format(i % 5000), i * 1.5, i % 7)).toArray
def size[T: scala.reflect.ClassTag](ser: org.apache.spark.serializer.Serializer, v: T): Int = ser.newInstance().serialize(v).limit()
val j = size(new JavaSerializer(conf), data)
val k = size(new KryoSerializer(conf), data)
val one = size(new JavaSerializer(conf), data.head)
val oneK = size(new KryoSerializer(conf), data.head)
println(s"RESULT java_total=$j kryo_total=$k java_one=$one kryo_one=$oneK rows=${data.length}")
System.exit(0)
