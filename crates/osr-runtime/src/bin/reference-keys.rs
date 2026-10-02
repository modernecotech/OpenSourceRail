fn main() {
    let rows:Vec<_>=[101_u64,102,900,901,902,1001,1002,1003].iter().map(|id|{
        serde_json::json!({"entity":id,"public_key":osr_runtime::reference_key(osr_core::EntityId(*id)).public().to_bytes().to_vec()})
    }).collect();
    println!("{}", serde_json::to_string(&rows).unwrap());
}
